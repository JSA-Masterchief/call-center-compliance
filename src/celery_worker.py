import os
from dotenv import load_dotenv
load_dotenv()

from celery import Celery
from src.transcriber import transcribe_audio
from src.analyzer import analyze_transcript

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "call_center",
    broker=REDIS_URL,
    backend=REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=3600,
)


@celery_app.task(bind=True, max_retries=2)
def process_audio_task(self, audio_base64: str, language: str) -> dict:
    try:
        transcript = transcribe_audio(audio_base64, language)
        if not transcript:
            raise ValueError("Transcription returned empty result.")

        analysis = analyze_transcript(transcript, language)

        return {
            "status": "success",
            "language": language,
            "transcript": transcript,
            "summary": analysis.get("summary", ""),
            "sop_validation": analysis.get("sop_validation", {}),
            "analytics": analysis.get("analytics", {}),
            "keywords": analysis.get("keywords", []),
        }
    except Exception as exc:
        raise self.retry(exc=exc, countdown=3)