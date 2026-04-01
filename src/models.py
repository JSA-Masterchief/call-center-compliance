from pydantic import BaseModel
from typing import List
from enum import Enum


class Language(str, Enum):
    TAMIL = "Tamil"
    HINDI = "Hindi"


class AudioFormat(str, Enum):
    MP3 = "mp3"


class PaymentPreference(str, Enum):
    EMI = "EMI"
    FULL_PAYMENT = "FULL_PAYMENT"
    PARTIAL_PAYMENT = "PARTIAL_PAYMENT"
    DOWN_PAYMENT = "DOWN_PAYMENT"


class RejectionReason(str, Enum):
    HIGH_INTEREST = "HIGH_INTEREST"
    BUDGET_CONSTRAINTS = "BUDGET_CONSTRAINTS"
    ALREADY_PAID = "ALREADY_PAID"
    NOT_INTERESTED = "NOT_INTERESTED"
    NONE = "NONE"


class Sentiment(str, Enum):
    POSITIVE = "Positive"
    NEGATIVE = "Negative"
    NEUTRAL = "Neutral"


class AdherenceStatus(str, Enum):
    FOLLOWED = "FOLLOWED"
    NOT_FOLLOWED = "NOT_FOLLOWED"


class CallAnalyticsRequest(BaseModel):
    language: Language
    audioFormat: AudioFormat
    audioBase64: str


class SOPValidation(BaseModel):
    greeting: bool
    identification: bool
    problemStatement: bool
    solutionOffering: bool
    closing: bool
    complianceScore: float
    adherenceStatus: AdherenceStatus
    explanation: str


class Analytics(BaseModel):
    paymentPreference: PaymentPreference
    rejectionReason: RejectionReason
    sentiment: Sentiment


class CallAnalyticsResponse(BaseModel):
    status: str
    language: str
    transcript: str
    summary: str
    sop_validation: SOPValidation
    analytics: Analytics
    keywords: List[str]