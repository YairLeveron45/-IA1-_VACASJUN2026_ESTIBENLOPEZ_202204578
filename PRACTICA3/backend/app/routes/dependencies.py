from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import AuthenticationError
from app.core.security import decode_access_token
from app.db.session import get_db_session
from app.models.user_model import User, UserRole
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService


bearer_scheme = HTTPBearer(auto_error=False)
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]
CredentialsDependency = Annotated[
    HTTPAuthorizationCredentials | None,
    Depends(bearer_scheme),
]


async def get_current_user(
    session: SessionDependency,
    credentials: CredentialsDependency,
) -> User:
    """Valida el Bearer token y carga al usuario activo de la solicitud."""
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = decode_access_token(credentials.credentials)
        user_id = int(payload["sub"])
        service = AuthService(UserRepository(session))
        return await service.get_authenticated_user(user_id)
    except (AuthenticationError, ValueError, TypeError) as exc:
        # Cualquier token inválido se responde como HTTP 401.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


CurrentUserDependency = Annotated[User, Depends(get_current_user)]


async def require_admin(current_user: CurrentUserDependency) -> User:
    """Restringe una ruta a usuarios con rol de administrador."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requieren permisos de administrador.",
        )
    return current_user


AdminUserDependency = Annotated[User, Depends(require_admin)]
