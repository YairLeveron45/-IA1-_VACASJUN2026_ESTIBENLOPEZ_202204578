from pydantic import BaseModel, Field


class AdminLoginPayload(BaseModel):
    password: str = Field(..., min_length=1)


class SymptomPayload(BaseModel):
    name: str = Field(..., min_length=1)


class FailurePayload(BaseModel):
    name: str = Field(..., min_length=1)


class RecommendationPayload(BaseModel):
    failure: str = Field(..., min_length=1)
    text: str = Field(..., min_length=1)


class RulePayload(BaseModel):
    failure: str = Field(..., min_length=1)
    symptoms: list[str] = Field(..., min_length=1)


class SystemConfigPayload(BaseModel):
    telegram_enabled: bool = True
    telegram_chat_id: str = ""
    telegram_message_template: str = Field(..., min_length=1)
