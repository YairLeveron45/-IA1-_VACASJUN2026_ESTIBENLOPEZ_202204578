from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import AuthenticationError
from app.core.security import hash_password
from app.models.user_model import User, UserRole
from app.schemas.auth_schema import LoginRequest
from app.services.auth_service import AuthService


@pytest.mark.asyncio
async def test_authenticate_active_user() -> None:
    repository = AsyncMock()
    now = datetime.now(UTC)
    repository.get_by_email.return_value = User(
        id=1,
        name="Administrador",
        email="admin@example.com",
        password_hash=hash_password("Admin123!"),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    service = AuthService(repository)

    response = await service.authenticate(
        LoginRequest(email="ADMIN@example.com", password="Admin123!")
    )

    assert response.token_type == "bearer"
    assert response.user.email == "admin@example.com"
    assert response.user.role == UserRole.ADMIN


@pytest.mark.asyncio
async def test_authenticate_rejects_wrong_password() -> None:
    repository = AsyncMock()
    now = datetime.now(UTC)
    repository.get_by_email.return_value = User(
        id=1,
        name="Administrador",
        email="admin@example.com",
        password_hash=hash_password("Admin123!"),
        role=UserRole.ADMIN,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    service = AuthService(repository)

    with pytest.raises(AuthenticationError):
        await service.authenticate(
            LoginRequest(email="admin@example.com", password="Wrong123!")
        )
