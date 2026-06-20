from fastapi import HTTPException, status

from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.user_model import User
from app.schemas.provider_schema import (
    ProviderCreate,
    ProviderListResponse,
    ProviderResponse,
    ProviderUpdate,
)
from app.services.provider_service import ProviderService


class ProviderController:
    """Expone el CRUD de proveedores y normaliza sus errores HTTP."""

    def __init__(self, service: ProviderService) -> None:
        self.service = service

    async def list(self, page: int, page_size: int) -> ProviderListResponse:
        items, total = await self.service.list(page, page_size)
        return ProviderListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get(self, provider_id: int) -> ProviderResponse:
        return await self._handle(self.service.get(provider_id))

    async def create(
        self,
        data: ProviderCreate,
        actor: User,
    ) -> ProviderResponse:
        return await self._handle(self.service.create(data, actor))

    async def update(
        self,
        provider_id: int,
        data: ProviderUpdate,
        actor: User,
    ) -> ProviderResponse:
        return await self._handle(
            self.service.update(provider_id, data, actor)
        )

    async def deactivate(
        self,
        provider_id: int,
        actor: User,
    ) -> ProviderResponse:
        return await self._handle(self.service.deactivate(provider_id, actor))

    async def _handle(self, operation) -> ProviderResponse:
        """Convierte ausencia y duplicados en HTTP 404 y 409."""
        try:
            return await operation
        except ResourceNotFoundError as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(exc),
            ) from exc
        except ResourceConflictError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=str(exc),
            ) from exc
