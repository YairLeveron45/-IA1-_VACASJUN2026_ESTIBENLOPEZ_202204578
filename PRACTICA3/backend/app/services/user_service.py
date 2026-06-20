from app.core.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.core.security import hash_password, verify_password
from app.models.user_model import User, UserRole
from app.repositories.user_repository import UserRepository
from app.schemas.user_schema import (
    OwnPasswordChange,
    PasswordChange,
    UserCreate,
    UserUpdate,
)
from app.services.processing_log_service import ProcessingLogService


class UserService:
    """Gestiona usuarios, roles, contraseñas y reglas administrativas."""

    def __init__(
        self,
        repository: UserRepository,
        audit: ProcessingLogService | None = None,
    ) -> None:
        self.repository = repository
        self.audit = audit

    async def list(self, page: int, page_size: int) -> tuple[list[User], int]:
        """Lista usuarios con paginación."""
        offset = (page - 1) * page_size
        return await self.repository.list(offset, page_size)

    async def get(self, user_id: int) -> User:
        """Obtiene un usuario o informa que no existe."""
        user = await self.repository.get_by_id(user_id)
        if user is None:
            raise ResourceNotFoundError("Usuario no encontrado.")
        return user

    async def create(
        self,
        data: UserCreate,
        actor: User | None = None,
    ) -> User:
        """Crea una cuenta activa evitando correos duplicados."""
        if await self.repository.get_by_email(str(data.email)):
            raise ResourceConflictError("Ya existe un usuario con ese correo.")

        user = User(
            name=data.name,
            email=str(data.email),
            password_hash=hash_password(data.password),
            role=data.role,
            is_active=True,
        )
        user = await self.repository.create(user)
        await self._record(
            "user_created",
            actor,
            f"Usuario creado: {user.email}, rol {user.role.value}.",
        )
        return user

    async def update(
        self,
        user_id: int,
        data: UserUpdate,
        acting_user: User,
    ) -> User:
        """Actualiza una cuenta protegiendo al administrador actual."""
        user = await self.get(user_id)
        changes = data.model_dump(exclude_unset=True)

        new_email = changes.get("email")
        if new_email and str(new_email) != user.email:
            existing = await self.repository.get_by_email(str(new_email))
            if existing:
                raise ResourceConflictError(
                    "Ya existe un usuario con ese correo."
                )
            changes["email"] = str(new_email)

        if user.id == acting_user.id:
            if changes.get("is_active") is False:
                raise BusinessRuleError(
                    "No puedes desactivar tu propia cuenta."
                )
            if changes.get("role") not in (None, UserRole.ADMIN):
                raise BusinessRuleError(
                    "No puedes retirar tu propio rol de administrador."
                )

        for field, value in changes.items():
            setattr(user, field, value)
        user = await self.repository.update(user)
        await self._record(
            "user_updated",
            acting_user,
            f"Usuario actualizado: {user.email}.",
        )
        return user

    async def deactivate(self, user_id: int, acting_user: User) -> User:
        """Desactiva una cuenta e impide la autodesactivación."""
        if user_id == acting_user.id:
            raise BusinessRuleError("No puedes desactivar tu propia cuenta.")

        user = await self.get(user_id)
        user.is_active = False
        user = await self.repository.update(user)
        await self._record(
            "user_deactivated",
            acting_user,
            f"Usuario desactivado: {user.email}.",
        )
        return user

    async def change_password(
        self,
        user_id: int,
        data: PasswordChange,
        acting_user: User | None = None,
    ) -> User:
        """Permite al administrador establecer una nueva contraseña."""
        user = await self.get(user_id)
        user.password_hash = hash_password(data.new_password)
        user = await self.repository.update(user)
        await self._record(
            "user_password_reset",
            acting_user,
            f"Contraseña restablecida para: {user.email}.",
        )
        return user

    async def change_own_password(
        self,
        user: User,
        data: OwnPasswordChange,
    ) -> User:
        """Cambia la contraseña propia después de validar la actual."""
        if not verify_password(data.current_password, user.password_hash):
            raise AuthenticationError("La contraseña actual es incorrecta.")
        if data.current_password == data.new_password:
            raise BusinessRuleError(
                "La nueva contraseña debe ser diferente de la actual."
            )

        user.password_hash = hash_password(data.new_password)
        user = await self.repository.update(user)
        await self._record(
            "own_password_changed",
            user,
            "El usuario cambió su propia contraseña.",
        )
        return user

    async def _record(
        self,
        action: str,
        actor: User | None,
        result: str,
    ) -> None:
        """Registra cambios administrativos cuando existe un actor."""
        if self.audit is not None and actor is not None:
            await self.audit.record(
                action=action,
                status="success",
                user_id=actor.id,
                result=result,
            )
