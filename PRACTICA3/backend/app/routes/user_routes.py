from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.user_controller import UserController
from app.db.session import get_db_session
from app.repositories.processing_log_repository import ProcessingLogRepository
from app.repositories.user_repository import UserRepository
from app.routes.dependencies import AdminUserDependency, CurrentUserDependency
from app.schemas.user_schema import (
    OwnPasswordChange,
    PasswordChange,
    UserCreate,
    UserListResponse,
    UserResponse,
    UserUpdate,
)
from app.services.user_service import UserService
from app.services.processing_log_service import ProcessingLogService


router = APIRouter(prefix="/users", tags=["Users"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> UserController:
    audit = ProcessingLogService(ProcessingLogRepository(session))
    return UserController(UserService(UserRepository(session), audit))


ControllerDependency = Annotated[UserController, Depends(get_controller)]


@router.get("", response_model=UserListResponse)
async def list_users(
    controller: ControllerDependency,
    _: AdminUserDependency,
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
) -> UserListResponse:
    return await controller.list(page, page_size)


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_user(
    data: UserCreate,
    controller: ControllerDependency,
    admin: AdminUserDependency,
) -> UserResponse:
    return await controller.create(data, admin)


@router.patch("/me/password", response_model=UserResponse)
async def change_own_password(
    data: OwnPasswordChange,
    controller: ControllerDependency,
    current_user: CurrentUserDependency,
) -> UserResponse:
    return await controller.change_own_password(current_user, data)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    controller: ControllerDependency,
    _: AdminUserDependency,
) -> UserResponse:
    return await controller.get(user_id)


@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    data: UserUpdate,
    controller: ControllerDependency,
    admin: AdminUserDependency,
) -> UserResponse:
    return await controller.update(user_id, data, admin)


@router.patch("/{user_id}/password", response_model=UserResponse)
async def reset_user_password(
    user_id: int,
    data: PasswordChange,
    controller: ControllerDependency,
    admin: AdminUserDependency,
) -> UserResponse:
    return await controller.change_password(user_id, data, admin)


@router.delete("/{user_id}", response_model=UserResponse)
async def deactivate_user(
    user_id: int,
    controller: ControllerDependency,
    admin: AdminUserDependency,
) -> UserResponse:
    return await controller.deactivate(user_id, admin)
