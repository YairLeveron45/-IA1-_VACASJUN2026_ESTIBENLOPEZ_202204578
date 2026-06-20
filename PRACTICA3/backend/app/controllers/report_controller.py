from collections.abc import Awaitable
from pathlib import Path
from typing import Any

from fastapi import HTTPException, status

from app.core.exceptions import (
    BusinessRuleError,
    InvalidFileError,
    ResourceNotFoundError,
)
from app.models.report_model import Report
from app.models.user_model import User
from app.schemas.email_schema import EmailSendResponse, ReportEmailRequest
from app.schemas.report_schema import (
    ReportCreate,
    ReportGenerationResponse,
    ReportListResponse,
)
from app.services.report_service import ReportService


class ReportController:
    """Expone reportes y traduce errores del dominio a HTTP."""

    def __init__(self, service: ReportService) -> None:
        self.service = service

    async def list(self, page: int, page_size: int) -> ReportListResponse:
        items, total = await self.service.list(page, page_size)
        return ReportListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def generate(
        self,
        data: ReportCreate,
        user: User,
    ) -> ReportGenerationResponse:
        return await self._handle(self.service.generate(data, user))

    async def get_download(self, report_id: int) -> tuple[Report, Path]:
        return await self._handle(self.service.get_download(report_id))

    async def send_email(
        self,
        report_id: int,
        data: ReportEmailRequest,
        user: User,
    ) -> EmailSendResponse:
        return await self._handle(
            self.service.send_email(report_id, data, user)
        )

    async def _handle(self, operation: Awaitable[Any]) -> Any:
        """Centraliza la respuesta para reportes inexistentes o no disponibles."""
        try:
            return await operation
        except ResourceNotFoundError as exc:
            # El reporte no existe.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except InvalidFileError as exc:
            # El registro existe, pero su archivo ya no está disponible.
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail=str(exc),
            ) from exc
        except BusinessRuleError as exc:
            # Un fallo externo, como SMTP, se representa como gateway inválido.
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(exc),
            ) from exc
