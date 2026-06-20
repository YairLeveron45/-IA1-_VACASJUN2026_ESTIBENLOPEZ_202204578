from fastapi import HTTPException, status

from app.core.exceptions import AuthenticationError
from app.schemas.auth_schema import LoginRequest, TokenResponse
from app.services.auth_service import AuthService


class AuthController:
    def __init__(self, service: AuthService) -> None:
        self.service = service

    async def login(self, credentials: LoginRequest) -> TokenResponse:
        try:
            return await self.service.authenticate(credentials)
        except AuthenticationError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(exc),
                headers={"WWW-Authenticate": "Bearer"},
            ) from exc
