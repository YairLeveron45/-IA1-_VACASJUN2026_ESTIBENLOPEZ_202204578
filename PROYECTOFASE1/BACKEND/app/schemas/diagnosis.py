from pydantic import BaseModel


class DiagnosisRequest(BaseModel):
    symptoms: list[str]
    notify_telegram: bool = False
    chat_id: str | None = None


class SymptomSuggestionRequest(BaseModel):
    symptoms: list[str]


class DiagnosisResponse(BaseModel):
    failure: str
    recommendation: str
    matched_symptoms: list[str]
    telegram_sent: bool = False


class DiagnosisHistoryItem(BaseModel):
    timestamp: str
    symptoms: list[str]
    failure: str
    recommendation: str
    telegram_sent: bool = False


class TelegramMessageRequest(BaseModel):
    chat_id: str
    message: str
