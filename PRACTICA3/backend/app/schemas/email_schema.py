from pydantic import BaseModel, EmailStr, Field


class ReportEmailRequest(BaseModel):
    recipient: EmailStr
    subject: str = Field(
        default="Reporte de facturas - SmartInvoice",
        min_length=3,
        max_length=180,
    )
    message: str = Field(
        default=(
            "Adjunto se encuentra el reporte solicitado desde SmartInvoice."
        ),
        min_length=3,
        max_length=2000,
    )


class EmailSendResponse(BaseModel):
    sent: bool
    delivery_mode: str
    recipient: EmailStr
    report_id: int
