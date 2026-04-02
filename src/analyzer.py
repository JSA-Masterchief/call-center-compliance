import os
import json
import logging
from dotenv import load_dotenv
load_dotenv()

from groq import Groq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ANALYSIS_PROMPT = """
You are an expert call center compliance analyst. Analyze the following call transcript and return a structured JSON response.

TRANSCRIPT:
{transcript}

LANGUAGE: {language}

Return ONLY valid JSON with this exact structure:

{{
  "summary": "Concise 2-3 sentence summary.",
  "sop_validation": {{
    "greeting": true or false,
    "identification": true or false,
    "problemStatement": true or false,
    "solutionOffering": true or false,
    "closing": true or false,
    "complianceScore": 0.0 to 1.0,
    "adherenceStatus": "FOLLOWED or NOT_FOLLOWED",
    "explanation": "Short explanation of what was and wasn't followed."
  }},
  "analytics": {{
    "paymentPreference": "EMI or FULL_PAYMENT or PARTIAL_PAYMENT or DOWN_PAYMENT",
    "rejectionReason": "HIGH_INTEREST or BUDGET_CONSTRAINTS or ALREADY_PAID or NOT_INTERESTED or NONE",
    "sentiment": "Positive or Negative or Neutral"
  }},
  "keywords": ["up to 10 important keywords from the transcript"]
}}

RULES:
- complianceScore = number of true SOP steps divided by 5
- adherenceStatus = FOLLOWED only if ALL 5 booleans are true
- rejectionReason = NONE if the call ended successfully
- Return ONLY the JSON object. No extra text, no markdown.
"""


def analyze_transcript(transcript: str, language: str) -> dict:
    logger.info(f"Starting analysis for language: {language}")
    logger.info(f"Transcript length: {len(transcript)} characters")
    
    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    prompt = ANALYSIS_PROMPT.format(transcript=transcript, language=language)

    try:
        logger.info("Calling Groq LLM...")
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": "You are a call center compliance analyst. Always respond with valid JSON only."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content.strip()
        logger.info("Groq LLM response received successfully")
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Error in analyze_transcript: {str(e)}")
        raise