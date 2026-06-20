from app.core.exceptions import ResourceConflictError, ResourceNotFoundError
from app.models.provider_model import Provider
from app.models.user_model import User
from app.repositories.provider_repository import ProviderRepository
from app.schemas.provider_schema import ProviderCreate, ProviderUpdate
from app.services.processing_log_service import ProcessingLogService


class ProviderService:
    """Implementa el CRUD y la auditoría de proveedores."""

    def __init__(
        self,
        repository: ProviderRepository,
        audit: ProcessingLogService | None = None,
    ) -> None:
        self.repository = repository
        self.audit = audit

    async def list(
        self,
        page: int,
        page_size: int,
    ) -> tuple[list[Provider], int]:
        """Lista proveedores con paginación."""
        offset = (page - 1) * page_size
        return await self.repository.list(offset=offset, limit=page_size)

    async def get(self, provider_id: int) -> Provider:
        """Obtiene un proveedor o informa que no existe."""
        provider = await self.repository.get_by_id(provider_id)
        if provider is None:
            raise ResourceNotFoundError("Proveedor no encontrado.")
        return provider

    async def create(
        self,
        data: ProviderCreate,
        actor: User | None = None,
    ) -> Provider:
        """Crea un proveedor evitando NIT duplicados."""
        if await self.repository.get_by_nit(data.nit):
            raise ResourceConflictError("Ya existe un proveedor con ese NIT.")

        provider = await self.repository.create(Provider(**data.model_dump()))
        await self._record(
            "provider_created",
            actor,
            f"Proveedor creado: {provider.name} ({provider.nit}).",
        )
        return provider

    async def update(
        self,
        provider_id: int,
        data: ProviderUpdate,
        actor: User | None = None,
    ) -> Provider:
        """Actualiza campos permitidos y controla conflictos de NIT."""
        provider = await self.get(provider_id)
        changes = data.model_dump(exclude_unset=True)

        new_nit = changes.get("nit")
        if new_nit and new_nit != provider.nit:
            existing = await self.repository.get_by_nit(new_nit)
            if existing:
                raise ResourceConflictError("Ya existe un proveedor con ese NIT.")

        for field, value in changes.items():
            setattr(provider, field, value)

        provider = await self.repository.update(provider)
        await self._record(
            "provider_updated",
            actor,
            f"Proveedor actualizado: {provider.name} ({provider.nit}).",
        )
        return provider

    async def deactivate(
        self,
        provider_id: int,
        actor: User | None = None,
    ) -> Provider:
        """Desactiva un proveedor sin borrar su historial."""
        provider = await self.get(provider_id)
        provider.is_active = False
        provider = await self.repository.update(provider)
        await self._record(
            "provider_deactivated",
            actor,
            f"Proveedor desactivado: {provider.name} ({provider.nit}).",
        )
        return provider

    async def _record(
        self,
        action: str,
        actor: User | None,
        result: str,
    ) -> None:
        """Registra la operación cuando existe un usuario responsable."""
        if self.audit is not None and actor is not None:
            await self.audit.record(
                action=action,
                status="success",
                user_id=actor.id,
                result=result,
            )
