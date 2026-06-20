from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.invoice_controller import InvoiceController
from app.db.session import get_db_session
from app.models.invoice_model import InvoiceStatus
from app.repositories.invoice_repository import InvoiceRepository
from app.repositories.provider_repository import ProviderRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.invoice_schema import (
    InvoiceDetailResponse,
    InvoiceListResponse,
    InvoiceResponse,
    InvoiceStatsResponse,
    InvoiceValidationRequest,
)
from app.schemas.ocr_schema import OcrProcessingResponse
from app.services.invoice_service import InvoiceService


router = APIRouter(prefix="/invoices", tags=["Invoices"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> InvoiceController:
    return InvoiceController(
        InvoiceService(
            InvoiceRepository(session),
            provider_repository=ProviderRepository(session),
        )
    )


ControllerDependency = Annotated[InvoiceController, Depends(get_controller)]


@router.get("", response_model=InvoiceListResponse)
async def list_invoices(
    controller: ControllerDependency,
    _: CurrentUserDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    invoice_status: InvoiceStatus | None = Query(default=None, alias="status"),
    provider_id: Annotated[int | None, Query(ge=1)] = None,
    search: Annotated[str | None, Query(min_length=1, max_length=160)] = None,
) -> InvoiceListResponse:
    return await controller.list(
        page,
        page_size,
        invoice_status,
        provider_id,
        search,
    )


@router.post(
    "/upload",
    response_model=InvoiceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_invoice(
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
    file: Annotated[UploadFile, File(description="PDF, JPG, JPEG o PNG")],
) -> InvoiceResponse:
    return await controller.upload(file, current_user)


@router.get("/stats", response_model=InvoiceStatsResponse)
async def invoice_stats(
    session: SessionDependency,
    _: CurrentUserDependency,
) -> InvoiceStatsResponse:
    return InvoiceStatsResponse(**await InvoiceRepository(session).stats())


@router.get("/{invoice_id}", response_model=InvoiceDetailResponse)
async def get_invoice(
    invoice_id: int,
    controller: ControllerDependency,
    _: CurrentUserDependency,
) -> InvoiceDetailResponse:
    return await controller.get(invoice_id)


@router.get("/{invoice_id}/download", response_class=FileResponse)
async def download_invoice(
    invoice_id: int,
    controller: ControllerDependency,
    _: CurrentUserDependency,
) -> FileResponse:
    invoice, path = await controller.get_download(invoice_id)
    return FileResponse(
        path=path,
        media_type=invoice.content_type,
        filename=invoice.file_name,
    )


@router.patch("/{invoice_id}/reject", response_model=InvoiceResponse)
async def reject_invoice(
    invoice_id: int,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> InvoiceResponse:
    return await controller.reject(invoice_id, current_user)


@router.delete("/{invoice_id}", response_model=InvoiceResponse)
async def delete_invoice(
    invoice_id: int,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> InvoiceResponse:
    return await controller.delete(invoice_id, current_user)


@router.post(
    "/{invoice_id}/process",
    response_model=OcrProcessingResponse,
)
async def process_invoice(
    invoice_id: int,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> OcrProcessingResponse:
    return await controller.process(invoice_id, current_user)


@router.patch(
    "/{invoice_id}/validate",
    response_model=InvoiceDetailResponse,
)
async def validate_invoice(
    invoice_id: int,
    data: InvoiceValidationRequest,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> InvoiceDetailResponse:
    return await controller.validate_manually(
        invoice_id,
        data,
        current_user,
    )
