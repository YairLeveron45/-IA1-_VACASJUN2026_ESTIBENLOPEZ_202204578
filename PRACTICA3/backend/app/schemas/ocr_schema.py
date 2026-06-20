from pydantic import BaseModel, Field

from app.schemas.invoice_schema import InvoiceDetailResponse


class ExtractedInvoiceData(BaseModel):
    invoice_number: str | None = None
    invoice_date: str | None = None
    provider_name: str | None = None
    nit: str | None = None
    subtotal: str | None = None
    taxes: str | None = None
    total: str | None = None


class OcrProcessingResponse(BaseModel):
    invoice: InvoiceDetailResponse
    extracted: ExtractedInvoiceData
    warnings: list[str] = Field(default_factory=list)
    pages_processed: int
