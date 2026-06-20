from datetime import datetime

from pydantic import BaseModel


class RpaExecutionResponse(BaseModel):
    success: bool
    invoice_id: int
    target_url: str
    confirmation: str
    evidence_file: str
    executed_at: datetime
