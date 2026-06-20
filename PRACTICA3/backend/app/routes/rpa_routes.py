from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.rpa_controller import RpaController
from app.db.session import get_db_session
from app.repositories.invoice_repository import InvoiceRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.rpa_schema import RpaExecutionResponse


router = APIRouter(prefix="/rpa", tags=["RPA"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> RpaController:
    return RpaController(InvoiceRepository(session))


ControllerDependency = Annotated[RpaController, Depends(get_controller)]


@router.post(
    "/invoices/{invoice_id}/execute",
    response_model=RpaExecutionResponse,
)
async def execute_invoice_rpa(
    invoice_id: int,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> RpaExecutionResponse:
    return await controller.execute(invoice_id, current_user)
