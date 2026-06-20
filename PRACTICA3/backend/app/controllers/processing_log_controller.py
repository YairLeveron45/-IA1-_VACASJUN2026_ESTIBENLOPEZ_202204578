from datetime import datetime

from fastapi import HTTPException, status

from app.core.exceptions import ResourceNotFoundError
from app.schemas.processing_log_schema import (
    ProcessingLogListResponse,
    ProcessingLogResponse,
)
from app.services.processing_log_service import ProcessingLogService


class ProcessingLogController:
    def __init__(self, service: ProcessingLogService) -> None:
        self.service = service

    async def list(
        self,
        page: int,
        page_size: int,
        invoice_id: int | None,
        user_id: int | None,
        action: str | None,
        log_status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> ProcessingLogListResponse:
        items, total = await self.service.list(
            page,
            page_size,
            invoice_id,
            user_id,
            action,
            log_status,
            date_from,
            date_to,
        )
        return ProcessingLogListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get(self, log_id: int) -> ProcessingLogResponse:
        try:
            return await self.service.get(log_id)
        except ResourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
