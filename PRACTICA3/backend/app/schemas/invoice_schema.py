from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from app.models.invoice_model import InvoiceStatus


class InvoiceResponse(BaseModel):
    id: int
    invoice_number: str | None
    invoice_date: date | None
    provider_id: int | None
    detected_provider_name: str | None
    detected_nit: str | None
    subtotal: Decimal | None
    taxes: Decimal | None
    total: Decimal | None
    file_name: str
    content_type: str
    status: InvoiceStatus
    uploaded_by_id: int | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class InvoiceDetailResponse(InvoiceResponse):
    ocr_text: str | None


class InvoiceListResponse(BaseModel):
    items: list[InvoiceResponse]
    total: int
    page: int
    page_size: int


class InvoiceStatsResponse(BaseModel):
    total: int
    pending: int
    processed: int
    error: int
    rejected: int


class InvoiceValidationRequest(BaseModel):
    invoice_number: str = Field(min_length=1, max_length=100)
    invoice_date: date
    provider_name: str = Field(min_length=2, max_length=160)
    nit: str = Field(min_length=2, max_length=30)
    subtotal: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    taxes: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    total: Decimal = Field(ge=0, max_digits=14, decimal_places=2)
    create_provider_if_missing: bool = False

    @field_validator("invoice_number", "provider_name", "nit", mode="before")
    @classmethod
    def strip_text(cls, value: str) -> str:
        return value.strip()

    @field_validator("nit")
    @classmethod
    def normalize_nit(cls, value: str) -> str:
        return value.upper().replace(" ", "")

    @model_validator(mode="after")
    def validate_amounts(self) -> "InvoiceValidationRequest":
        difference = abs((self.subtotal + self.taxes) - self.total)
        if difference > Decimal("0.05"):
            raise ValueError(
                "El total debe coincidir con subtotal más impuestos."
            )
        return self
