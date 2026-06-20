from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.core.exceptions import BusinessRuleError, ResourceConflictError
from app.core.security import hash_password, verify_password
from app.models.user_model import User, UserRole
from app.schemas.user_schema import OwnPasswordChange, UserCreate, UserUpdate
from app.services.user_service import UserService


def make_user(user_id: int = 1, role: UserRole = UserRole.ADMIN) -> User:
    now = datetime.now(UTC)
    return User(
        id=user_id,
        name="Usuario",
        email=f"user{user_id}@example.com",
        password_hash=hash_password("Current123!"),
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.asyncio
async def test_create_user_hashes_password() -> None:
    repository = AsyncMock()
    repository.get_by_email.return_value = None
    repository.create.side_effect = lambda user: user
    service = UserService(repository)

    user = await service.create(
        UserCreate(
            name="Operador",
            email="operator@example.com",
            password="Operator123!",
        )
    )

    assert user.password_hash != "Operator123!"
    assert verify_password("Operator123!", user.password_hash)
    assert user.role == UserRole.OPERATOR


@pytest.mark.asyncio
async def test_create_user_rejects_duplicate_email() -> None:
    repository = AsyncMock()
    repository.get_by_email.return_value = make_user()
    service = UserService(repository)

    with pytest.raises(ResourceConflictError):
        await service.create(
            UserCreate(
                name="Duplicado",
                email="user1@example.com",
                password="Duplicate123!",
            )
        )


@pytest.mark.asyncio
async def test_admin_cannot_deactivate_self() -> None:
    repository = AsyncMock()
    admin = make_user()
    service = UserService(repository)

    with pytest.raises(BusinessRuleError):
        await service.deactivate(admin.id, admin)


@pytest.mark.asyncio
async def test_admin_cannot_remove_own_role() -> None:
    repository = AsyncMock()
    admin = make_user()
    repository.get_by_id.return_value = admin
    service = UserService(repository)

    with pytest.raises(BusinessRuleError):
        await service.update(
            admin.id,
            UserUpdate(role=UserRole.OPERATOR),
            admin,
        )


@pytest.mark.asyncio
async def test_user_changes_own_password() -> None:
    repository = AsyncMock()
    repository.update.side_effect = lambda user: user
    user = make_user()
    service = UserService(repository)

    result = await service.change_own_password(
        user,
        OwnPasswordChange(
            current_password="Current123!",
            new_password="NewPassword123!",
        ),
    )

    assert verify_password("NewPassword123!", result.password_hash)
