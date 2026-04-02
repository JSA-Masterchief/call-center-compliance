# CallIQ — Call Center Compliance API

> AI-powered call center analytics for Hindi (Hinglish) & Tamil (Tanglish) voice recordings.
> Built for GUVI HCL Hackathon — Track 3: Call Center Compliance.

---

## Description

CallIQ is an intelligent API that processes call center audio recordings, transcribes them using
Groq Whisper, and performs multi-stage AI analysis using Groq LLaMA-3.3-70b — producing SOP
compliance scores, payment classification, sentiment analysis, keyword extraction, and vector
storage for semantic search.

**Strategy:** A single LLaMA-3.3-70b structured prompt handles all NLP tasks simultaneously
(summary, SOP validation, analytics, keywords), minimizing latency while maximizing accuracy.
Transcripts are stored in an in-memory vector index using sentence embeddings for semantic search.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI (Python 3.11) |
| Speech-to-Text | Groq Whisper API (whisper-large-v3) |
| NLP / Analysis | Groq LLaMA (llama-3.3-70b-versatile) |
| Vector Storage | FAISS + sentence-transformers |
| Async Processing | Celery + Redis |
| Frontend UI | Vanilla HTML/CSS/JS |
| Deployment | Render |

---

## Architecture Overview
```
POST /api/call-analytics
        │
        ▼
  Auth Middleware (x-api-key header)
        │
        ▼
  Base64 Decode → MP3 bytes (temp file)
        │
        ▼
  Groq Whisper API → Full Transcript
        │
        ▼
  Groq LLaMA-3.3-70b (Single Structured Prompt)
    ├── Summary (2-3 sentences)
    ├── SOP Validation (5 booleans + score + status)
    ├── Payment Classification (EMI/FULL/PARTIAL/DOWN)
    ├── Rejection Reason (5 categories)
    ├── Sentiment (Positive/Negative/Neutral)
    └── Keywords (up to 10)
        │
        ▼
  Vector Storage (FAISS index)
    └── Transcript embedded + stored for semantic search
        │
        ▼
  Structured JSON Response
```

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/JSA-Masterchief/call-center-compliance.git
cd call-center-compliance
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set environment variables
```bash
cp .env.example .env
# Edit .env and add your keys
```

### 4. Run the application
```bash
# Terminal 1 — Start API
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal 2 — Start Celery worker (optional for local async)
celery -A src.celery_worker:celery_app worker --loglevel=info --pool=solo
```

### 5. Open UI
Visit `http://localhost:8000` in your browser.

---

## API Usage

### Endpoint
```
POST /api/call-analytics
```

### Headers
```
Content-Type: application/json
x-api-key: YOUR_API_KEY
```

### Request Body
```json
{
  "language": "Tamil",
  "audioFormat": "mp3",
  "audioBase64": "<base64-encoded-mp3>"
}
```

### Example cURL
```bash
AUDIO_B64=$(base64 -w 0 sample.mp3)

curl -X POST https://call-center-compliance.onrender.com/api/call-analytics \
  -H "Content-Type: application/json" \
  -H "x-api-key: sk_track3_987654321" \
  -d "{\"language\": \"Tamil\", \"audioFormat\": \"mp3\", \"audioBase64\": \"$AUDIO_B64\"}"
```

### Success Response
```json
{
  "status": "success",
  "language": "Tamil",
  "transcript": "...",
  "summary": "...",
  "sop_validation": {
    "greeting": true,
    "identification": false,
    "problemStatement": true,
    "solutionOffering": true,
    "closing": true,
    "complianceScore": 0.8,
    "adherenceStatus": "NOT_FOLLOWED",
    "explanation": "..."
  },
  "analytics": {
    "paymentPreference": "EMI",
    "rejectionReason": "NONE",
    "sentiment": "Positive"
  },
  "keywords": ["Data Science", "EMI", "Guvi", "IIT Madras"]
}
```

### Error Responses
```json
{ "detail": "Unauthorized: Invalid API Key" }   // 401
{ "detail": "Invalid or missing audioBase64" }   // 400
{ "status": "error", "message": "..." }          // 500
```

---

## Environment Variables

| Variable | Description |
|---|---|
| `GROQ_API_KEY` | Groq API key for Whisper + LLaMA |
| `API_KEY` | Secret key to protect your endpoint |
| `REDIS_URL` | Redis connection URL (for Celery) |

---

## AI Tools Used

| Tool | Purpose |
|---|---|
| **Claude (Anthropic)** | Code architecture, prompt engineering, UI design assistance |
| **Groq Whisper (whisper-large-v3)** | Speech-to-text transcription for Hindi and Tamil audio |
| **Groq LLaMA (llama-3.3-70b-versatile)** | NLP analysis — summarisation, SOP validation, payment classification, sentiment, keywords |

---

## Known Limitations

- Very short or silent audio files may produce empty transcripts
- Heavily mixed code-switching audio may reduce Whisper accuracy
- Free Render tier spins down after inactivity — first request may take 50 seconds to wake up
- Vector storage is in-memory and resets on server restart
- FAISS index not persisted to disk in current version

---

## Project Structure
```
call-center-compliance/
├── src/
│   ├── main.py            # FastAPI app + /api/call-analytics endpoint
│   ├── models.py          # Pydantic request/response models
│   ├── transcriber.py     # Groq Whisper STT integration
│   ├── analyzer.py        # Groq LLaMA NLP analysis
│   ├── vector_store.py    # FAISS vector storage for transcripts
│   └── celery_worker.py   # Async task processing
├── static/
│   └── index.html         # Dashboard UI
├── requirements.txt
├── runtime.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```