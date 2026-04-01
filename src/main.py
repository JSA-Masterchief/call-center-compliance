import os
import time
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.models import CallAnalyticsRequest
from src.celery_worker import process_audio_task

load_dotenv()

API_KEY = os.getenv("API_KEY", "sk_track3_987654321")

app = FastAPI(title="Call Center Compliance API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_ui():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/health")
async def health_check():
    return {"status": "ok"}


@app.post("/api/call-analytics")
async def call_analytics(
    request: CallAnalyticsRequest,
    x_api_key: str = Header(...),
):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")

    if not request.audioBase64 or len(request.audioBase64) < 100:
        raise HTTPException(status_code=400, detail="Invalid or missing audioBase64")

    try:
        task = process_audio_task.delay(request.audioBase64, request.language.value)

        start = time.time()
        while not task.ready():
            if time.time() - start > 120:
                raise HTTPException(status_code=504, detail="Processing timeout. Retry.")
            time.sleep(0.5)

        result = task.get()
        return JSONResponse(content=result, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
        )