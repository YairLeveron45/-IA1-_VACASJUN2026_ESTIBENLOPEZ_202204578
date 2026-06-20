from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.provider_controller import ProviderController
from app.db.session import get_db_session
from app.repositories.processing_log_repository import ProcessingLogRepository
from app.repositories.provider_repository import ProviderRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.provider_schema import (
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderUpdate,
)
from app.services.provider_service import ProviderService
from app.services.processing_log_service import ProcessingLogService


router = APIRouter(prefix="/providers", tags=["Providers"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> ProviderController:
    repository = ProviderRepository(session)
    audit = ProcessingLogService(ProcessingLogRepository(session))
    service = ProviderService(repository, audit)
    return ProviderController(service)


ControllerDependency = Annotated[ProviderController, Depends(get_controller)]


@router.get("/lookup", response_model=ProviderResponse | None)
async def lookup_provider(
    nit: Annotated[str, Query(min_length=2, max_length=30)],
    session: SessionDependency,
    _: CurrentUserDependency,
) -> ProviderResponse | None:
    normalized_nit = nit.upper().replace(" ", "")
    return await ProviderRepository(session).get_by_nit(normalized_nit)


@router.get("", response_model=ProviderListResponse)
async def list_providers(
    controller: ControllerDependency,
    _: CurrentUserDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> ProviderListResponse:
    return await controller.list(page, page_size)


@router.get("/{provider_id}", response_model=ProviderResponse)
async def get_provider(
    provider_id: int,
    controller: ControllerDependency,
    _: CurrentUserDependency,
) -> ProviderResponse:
    return await controller.get(provider_id)


@router.post(
    "",
    response_model=ProviderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_provider(
    data: ProviderCreate,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> ProviderResponse:
    return await controller.create(data, current_user)


@router.patch("/{provider_id}", response_model=ProviderResponse)
async def update_provider(
    provider_id: int,
    data: ProviderUpdate,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> ProviderResponse:
    return await controller.update(provider_id, data, current_user)


@router.delete("/{provider_id}", response_model=ProviderResponse)
async def deactivate_provider(
    provider_id: int,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> ProviderResponse:
    return await controller.deactivate(provider_id, current_user)
