from collections.abc import Awaitable
from typing import Any

from fastapi import HTTPException, status

from app.core.exceptions import (
    AuthenticationError,
    BusinessRuleError,
    ResourceConflictError,
    ResourceNotFoundError,
)
from app.models.user_model import User
from app.schemas.user_schema import (
    OwnPasswordChange,
    PasswordChange,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService


class UserController:
    """Expone operaciones administrativas de usuarios."""

    def __init__(self, service: UserService) -> None:
        self.service = service

    async def list(self, page: int, page_size: int) -> UserListResponse:
        items, total = await self.service.list(page, page_size)
        return UserListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
        )

    async def get(self, user_id: int) -> UserResponse:
        return await self._handle(self.service.get(user_id))

    async def create(
        self,
        data: UserCreate,
        actor: User,
    ) -> UserResponse:
        return await self._handle(self.service.create(data, actor))

    async def update(
        self,
        user_id: int,
        data: UserUpdate,
        acting_user: User,
    ) -> UserResponse:
        return await self._handle(
            self.service.update(user_id, data, acting_user)
        )

    async def deactivate(
        self,
        user_id: int,
        acting_user: User,
    ) -> UserResponse:
        return await self._handle(
            self.service.deactivate(user_id, acting_user)
        )

    async def change_password(
        self,
        user_id: int,
        data: PasswordChange,
        acting_user: User,
    ) -> UserResponse:
        return await self._handle(
            self.service.change_password(user_id, data, acting_user)
        )

    async def change_own_password(
        self,
        user: User,
        data: OwnPasswordChange,
    ) -> UserResponse:
        return await self._handle(
            self.service.change_own_password(user, data)
        )

    async def _handle(self, operation: Awaitable[Any]) -> UserResponse:
        """Traduce errores de usuario a códigos HTTP adecuados."""
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
        except BusinessRuleError as exc:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(exc),
            ) from exc
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
            ) from exc
