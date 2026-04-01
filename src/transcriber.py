import base64
import tempfile
import os
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

LANGUAGE_MAP = {
    "Tamil": "ta",
    "Hindi": "hi",
}


def transcribe_audio(audio_base64: str, language: str) -> str:
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    audio_bytes = base64.b64decode(audio_base64)

    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp_file:
        tmp_file.write(audio_bytes)
        tmp_path = tmp_file.name

    try:
        whisper_lang = LANGUAGE_MAP.get(language, None)
        with open(tmp_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-large-v3",
                file=audio_file,
                language=whisper_lang,
                response_format="text",
            )
        return response.strip()
    finally:
        os.unlink(tmp_path)