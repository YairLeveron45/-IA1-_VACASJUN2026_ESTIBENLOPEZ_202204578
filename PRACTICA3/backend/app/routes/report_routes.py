from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.report_controller import ReportController
from app.db.session import get_db_session
from app.repositories.report_repository import ReportRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.email_schema import EmailSendResponse, ReportEmailRequest
from app.schemas.report_schema import (
    ReportCreate,
    ReportGenerationResponse,
    ReportListResponse,
)
from app.services.report_service import ReportService


router = APIRouter(prefix="/reports", tags=["Reports"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> ReportController:
    return ReportController(ReportService(ReportRepository(session)))


ControllerDependency = Annotated[ReportController, Depends(get_controller)]


@router.get("", response_model=ReportListResponse)
async def list_reports(
    controller: ControllerDependency,
    _: CurrentUserDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ReportListResponse:
    return await controller.list(page, page_size)


@router.post(
    "",
    response_model=ReportGenerationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def generate_report(
    data: ReportCreate,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> ReportGenerationResponse:
    return await controller.generate(data, current_user)


@router.get("/{report_id}/download", response_class=FileResponse)
async def download_report(
    report_id: int,
    controller: ControllerDependency,
    _: CurrentUserDependency,
) -> FileResponse:
    report, path = await controller.get_download(report_id)
    media_type = (
        "text/csv; charset=utf-8"
        if report.file_format == "csv"
        else "application/pdf"
    )
    return FileResponse(
        path=path,
        media_type=media_type,
        filename=f"smartinvoice-report-{report.id}.{report.file_format}",
    )


@router.post(
    "/{report_id}/email",
    response_model=EmailSendResponse,
)
async def email_report(
    report_id: int,
    data: ReportEmailRequest,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> EmailSendResponse:
    return await controller.send_email(report_id, data, current_user)
