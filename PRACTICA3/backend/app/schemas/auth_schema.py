from pydantic import BaseModel, EmailStr, Field, field_validator

from app.models.user_model import UserRole
from app.schemas.user_schema import UserResponse


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: str) -> str:
        return value.strip().lower()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user: UserResponse


class TokenPayload(BaseModel):
    sub: str
    type: str
    role: UserRole | None = None
