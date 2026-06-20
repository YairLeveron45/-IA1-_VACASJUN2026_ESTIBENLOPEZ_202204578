from collections.abc import Awaitable
from pathlib import Path
from typing import Any

from fastapi import HTTPException, UploadFile, status

from app.core.exceptions import (
    BusinessRuleError,
    InvalidFileError,
    ResourceNotFoundError,
)
from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.user_model import User
from app.schemas.invoice_schema import (
    InvoiceDetailResponse,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceValidationRequest,
)
from app.schemas.ocr_schema import OcrProcessingResponse
from app.services.invoice_service import InvoiceService


class InvoiceController:
    """Adapta las operaciones de facturas a respuestas HTTP."""

    def __init__(self, service: InvoiceService) -> None:
        self.service = service

    async def list(
        self,
        page: int,
        page_size: int,
        invoice_status: InvoiceStatus | None,
        provider_id: int | None,
        search: str | None,
    ) -> InvoiceListResponse:
        items, total = await self.service.list(
            page,
            page_size,
            invoice_status,
            provider_id,
            search,
        )
        return InvoiceListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get(self, invoice_id: int) -> InvoiceDetailResponse:
        return await self._handle(self.service.get(invoice_id))

    async def upload(self, file: UploadFile, user: User) -> InvoiceResponse:
        return await self._handle(self.service.upload(file, user))

    async def get_download(
        self,
        invoice_id: int,
    ) -> tuple[Invoice, Path]:
        return await self._handle(self.service.get_download(invoice_id))

    async def reject(self, invoice_id: int, user: User) -> InvoiceResponse:
        return await self._handle(self.service.reject(invoice_id, user))

    async def delete(self, invoice_id: int, user: User) -> InvoiceResponse:
        return await self._handle(self.service.delete(invoice_id, user))

    async def process(
        self,
        invoice_id: int,
        user: User,
    ) -> OcrProcessingResponse:
        return await self._handle(self.service.process(invoice_id, user))

    async def validate_manually(
        self,
        invoice_id: int,
        data: InvoiceValidationRequest,
        user: User,
    ) -> InvoiceDetailResponse:
        return await self._handle(
            self.service.validate_manually(invoice_id, data, user)
        )

    async def _handle(self, operation: Awaitable[Any]) -> Any:
        """Convierte errores del dominio en códigos HTTP comprensibles."""
        try:
            return await operation
        except ResourceNotFoundError as exc:
            # Un recurso inexistente corresponde a HTTP 404.
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except (BusinessRuleError, InvalidFileError) as exc:
            # Validaciones de negocio o archivo se reportan como solicitud inválida.
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
