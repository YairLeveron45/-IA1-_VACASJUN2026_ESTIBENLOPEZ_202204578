from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.controllers.auth_controller import AuthController
from app.db.session import get_db_session
from app.repositories.user_repository import UserRepository
from app.routes.dependencies import CurrentUserDependency
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.schemas.user_schema import UserResponse
from app.services.auth_service import AuthService


router = APIRouter(prefix="/auth", tags=["Authentication"])
SessionDependency = Annotated[AsyncSession, Depends(get_db_session)]


def get_controller(session: SessionDependency) -> AuthController:
    repository = UserRepository(session)
    service = AuthService(repository)
    return AuthController(service)


ControllerDependency = Annotated[AuthController, Depends(get_controller)]


@router.post("/login", response_model=TokenResponse)
async def login(
    credentials: LoginRequest,
    controller: ControllerDependency,
) -> TokenResponse:
    return await controller.login(credentials)


@router.get("/me", response_model=UserResponse)
async def get_profile(current_user: CurrentUserDependency) -> UserResponse:
    return current_user
