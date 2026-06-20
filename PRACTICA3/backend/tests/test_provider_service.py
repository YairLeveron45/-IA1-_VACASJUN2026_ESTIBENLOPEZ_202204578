from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.provider_model import Provider
from app.schemas.provider_schema import ProviderCreate, ProviderUpdate
from app.services.provider_service import ProviderService


@pytest.mark.asyncio
async def test_create_provider_normalizes_nit() -> None:
    repository = AsyncMock()
    repository.get_by_nit.return_value = None
    repository.create.side_effect = lambda provider: provider
    service = ProviderService(repository)
    data = ProviderCreate(name="Proveedor Uno", nit=" 1234 k ")

    provider = await service.create(data)

    assert provider.name == "Proveedor Uno"
    assert provider.nit == "1234K"
    repository.create.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_provider_rejects_duplicate_nit() -> None:
    repository = AsyncMock()
    repository.get_by_nit.return_value = Provider(name="Existente", nit="1234K")
    service = ProviderService(repository)
    data = ProviderCreate(name="Duplicado", nit="1234K")

    with pytest.raises(ResourceConflictError):
        await service.create(data)

    repository.create.assert_not_awaited()


@pytest.mark.asyncio
async def test_update_missing_provider_returns_not_found() -> None:
    repository = AsyncMock()
    repository.get_by_id.return_value = None
    service = ProviderService(repository)

    with pytest.raises(ResourceNotFoundError):
        await service.update(999, ProviderUpdate(name="Nuevo nombre"))


@pytest.mark.asyncio
async def test_deactivate_provider_uses_soft_delete() -> None:
    repository = AsyncMock()
    provider = Provider(name="Proveedor Uno", nit="1234K", is_active=True)
    repository.get_by_id.return_value = provider
    repository.update.side_effect = lambda item: item
    service = ProviderService(repository)

    result = await service.deactivate(1)

    assert result.is_active is False
    repository.update.assert_awaited_once_with(provider)
