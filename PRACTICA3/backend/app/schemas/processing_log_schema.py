from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ProcessingLogResponse(BaseModel):
    id: int
    invoice_id: int | None
    user_id: int | None
    action: str
    status: str
    result: str | None
    error_detail: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ProcessingLogListResponse(BaseModel):
    items: list[ProcessingLogResponse]
    total: int
    page: int
    page_size: int
