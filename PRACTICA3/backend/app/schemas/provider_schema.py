from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator


class ProviderBase(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    nit: str = Field(min_length=2, max_length=30)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=300)

    @field_validator("name", "nit", "phone", "address", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @field_validator("nit")
    @classmethod
    def normalize_nit(cls, value: str) -> str:
        return value.upper().replace(" ", "")


class ProviderCreate(ProviderBase):
    pass


class ProviderUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    nit: str | None = Field(default=None, min_length=2, max_length=30)
    email: EmailStr | None = None
    phone: str | None = Field(default=None, max_length=30)
    address: str | None = Field(default=None, max_length=300)
    is_active: bool | None = None

    @field_validator("name", "nit", "phone", "address", mode="before")
    @classmethod
    def strip_text(cls, value: str | None) -> str | None:
        return value.strip() if isinstance(value, str) else value

    @field_validator("nit")
    @classmethod
    def normalize_nit(cls, value: str | None) -> str | None:
        return value.upper().replace(" ", "") if value else value


class ProviderResponse(ProviderBase):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProviderListResponse(BaseModel):
    items: list[ProviderResponse]
    total: int
    page: int
    page_size: int
