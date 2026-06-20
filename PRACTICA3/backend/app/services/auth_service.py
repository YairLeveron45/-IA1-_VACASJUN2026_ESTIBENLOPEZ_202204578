from app.core.config import settings
from app.core.exceptions import AuthenticationError
from app.core.security import create_access_token, verify_password
from app.models.user_model import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth_schema import LoginRequest, TokenResponse


class AuthService:
    """Gestiona autenticación, estado del usuario y emisión de tokens."""

    def __init__(self, repository: UserRepository) -> None:
        self.repository = repository

    async def authenticate(self, credentials: LoginRequest) -> TokenResponse:
        """Valida credenciales activas y devuelve un token JWT."""
        user = await self.repository.get_by_email(str(credentials.email))
        if user is None or not verify_password(
            credentials.password,
            user.password_hash,
        ):
            raise AuthenticationError("Correo o contraseña incorrectos.")

        if not user.is_active:
            raise AuthenticationError("El usuario se encuentra desactivado.")

        token = create_access_token(
            subject=str(user.id),
            extra_claims={"role": user.role.value},
        )
        return TokenResponse(
            access_token=token,
            expires_in=settings.access_token_expire_minutes * 60,
            user=user,
        )

    async def get_authenticated_user(self, user_id: int) -> User:
        """Recupera el usuario del token y rechaza cuentas inválidas o inactivas."""
        user = await self.repository.get_by_id(user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("Usuario no válido.")
        return user
