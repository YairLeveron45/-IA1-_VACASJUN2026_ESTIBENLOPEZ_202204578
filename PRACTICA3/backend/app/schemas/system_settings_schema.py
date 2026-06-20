from pydantic import BaseModel


class SystemSettingsResponse(BaseModel):
    application: str
    environment: str
    debug: bool
    api_prefix: str
    access_token_expire_minutes: int
    max_upload_size_mb: int
    allowed_invoice_formats: list[str]
    tesseract_language: str
    smtp_enabled: bool
    smtp_delivery_mode: str
    smtp_from_email: str
    rpa_enabled: bool
    rpa_target_url: str
    database_engine: str
