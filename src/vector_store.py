import os
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# In-memory vector store (no external dependencies needed)
# Stores transcripts with metadata for semantic search
_transcript_store = []


def store_transcript(transcript: str, language: str, summary: str, keywords: list) -> str:
    """
    Store transcript in the in-memory vector store.
    Returns the document ID.
    """
    try:
        doc_id = f"transcript_{len(_transcript_store) + 1}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        document = {
            "id": doc_id,
            "transcript": transcript,
            "language": language,
            "summary": summary,
            "keywords": keywords,
            "timestamp": datetime.now().isoformat(),
            "word_count": len(transcript.split()),
        }
        
        _transcript_store.append(document)
        logger.info(f"Stored transcript {doc_id} in vector store. Total: {len(_transcript_store)}")
        return doc_id

    except Exception as e:
        logger.error(f"Error storing transcript: {str(e)}")
        return "storage_failed"


def search_transcripts(query: str, top_k: int = 5) -> list:
    """
    Simple keyword-based semantic search over stored transcripts.
    Returns top_k most relevant transcripts.
    """
    if not _transcript_store:
        return []

    query_words = set(query.lower().split())
    scored = []

    for doc in _transcript_store:
        text = (doc["transcript"] + " " + doc["summary"]).lower()
        text_words = set(text.split())
        
        # Score = number of query words found in document
        score = len(query_words.intersection(text_words))
        if score > 0:
            scored.append({
                "id": doc["id"],
                "score": score,
                "summary": doc["summary"],
                "language": doc["language"],
                "keywords": doc["keywords"],
                "timestamp": doc["timestamp"],
            })

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[:top_k]


def get_store_stats() -> dict:
    """Return stats about the vector store."""
    return {
        "total_transcripts": len(_transcript_store),
        "languages": list(set(d["language"] for d in _transcript_store)),
    }