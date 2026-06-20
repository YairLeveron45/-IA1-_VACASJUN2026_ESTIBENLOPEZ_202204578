from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

from app.models.invoice_model import InvoiceStatus


class ReportFormat(StrEnum):
    CSV = "csv"
    PDF = "pdf"


class ReportCreate(BaseModel):
    file_format: ReportFormat
    date_from: date | None = None
    date_to: date | None = None
    provider_id: int | None = Field(default=None, ge=1)
    status: InvoiceStatus | None = None

    @model_validator(mode="after")
    def validate_dates(self) -> "ReportCreate":
        if self.date_from and self.date_to and self.date_from > self.date_to:
            raise ValueError(
                "La fecha inicial no puede ser posterior a la fecha final."
            )
        return self


class ReportResponse(BaseModel):
    id: int
    report_type: str
    file_format: str
    generated_by_id: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ReportListResponse(BaseModel):
    items: list[ReportResponse]
    total: int
    page: int
    page_size: int


class ReportGenerationResponse(BaseModel):
    report: ReportResponse
    invoice_count: int
    automatic_email_sent: bool
    automatic_email_recipient: EmailStr
    automatic_email_delivery_mode: str | None = None
    automatic_email_error: str | None = None
