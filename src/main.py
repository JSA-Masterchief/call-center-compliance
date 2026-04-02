import os
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.models import CallAnalyticsRequest
from src.transcriber import transcribe_audio
from src.analyzer import analyze_transcript
from src.vector_store import store_transcript, search_transcripts, get_store_stats

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
    stats = get_store_stats()
    return {"status": "ok", "vector_store": stats}


@app.get("/api/search")
async def search(query: str, x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Unauthorized")
    results = search_transcripts(query)
    return {"query": query, "results": results}


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
        # Step 1 — Transcribe
        transcript = transcribe_audio(request.audioBase64, request.language.value)
        if not transcript:
            raise ValueError("Transcription returned empty result.")

        # Step 2 — Analyze
        analysis = analyze_transcript(transcript, request.language.value)

        # Step 3 — Store in vector store
        doc_id = store_transcript(
            transcript=transcript,
            language=request.language.value,
            summary=analysis.get("summary", ""),
            keywords=analysis.get("keywords", []),
        )

        return JSONResponse(content={
            "status": "success",
            "language": request.language.value,
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "sop_validation": analysis.get("sop_validation", {}),
            "analytics": analysis.get("analytics", {}),
            "keywords": analysis.get("keywords", []),
        }, status_code=200)

    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            content={"status": "error", "message": str(e)},
            status_code=500,
        )