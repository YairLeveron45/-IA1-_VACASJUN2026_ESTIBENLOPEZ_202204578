from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.processing_log_controller import ProcessingLogController
from app.db.session import get_db_session
from app.repositories.processing_log_repository import ProcessingLogRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.processing_log_schema import (
    ProcessingLogListResponse,
    ProcessingLogResponse,
)
from app.services.processing_log_service import ProcessingLogService


router = APIRouter(prefix="/logs", tags=["Processing logs"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> ProcessingLogController:
    repository = ProcessingLogRepository(session)
    return ProcessingLogController(ProcessingLogService(repository))


ControllerDependency = Annotated[
    ProcessingLogController,
    Depends(get_controller),
]


@router.get("", response_model=ProcessingLogListResponse)
async def list_logs(
    controller: ControllerDependency,
    _: CurrentUserDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    invoice_id: Annotated[int | None, Query(ge=1)] = None,
    user_id: Annotated[int | None, Query(ge=1)] = None,
    action: Annotated[str | None, Query(max_length=100)] = None,
    log_status: Annotated[
        str | None,
        Query(alias="status", max_length=30),
    ] = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> ProcessingLogListResponse:
    if date_from and date_to and date_from > date_to:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La fecha inicial no puede ser posterior a la fecha final.",
        )
    return await controller.list(
        page,
        page_size,
        invoice_id,
        user_id,
        action,
        log_status,
        date_from,
        date_to,
    )


@router.get("/{log_id}", response_model=ProcessingLogResponse)
async def get_log(
    log_id: int,
    controller: ControllerDependency,
    _: CurrentUserDependency,
) -> ProcessingLogResponse:
    return await controller.get(log_id)
