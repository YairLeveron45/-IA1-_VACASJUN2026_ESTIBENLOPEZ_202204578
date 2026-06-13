from pydantic import BaseModel


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class AdminUserCreate(BaseModel):
    username: str
    password: str


class CategoryCreate(BaseModel):
    name: str
    description: str = ""


class CategoryUpdate(BaseModel):
    name: str
    description: str = ""


class FAQCreate(BaseModel):
    question: str
    answer: str
    category_id: int
    active: bool = True


class SettingUpdate(BaseModel):
    telegram_chat_id: str = ""


class BotQuery(BaseModel):
    query: str
    telegram_user: str = ""


class BotResponse(BaseModel):
    answer: str
    found: bool
