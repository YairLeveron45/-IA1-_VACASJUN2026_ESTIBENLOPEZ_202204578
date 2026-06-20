from fastapi import APIRouter

from app.controllers.health_controller import HealthController
from app.schemas.health_schema import HealthResponse


router = APIRouter(prefix="/health", tags=["Health"])
controller = HealthController()


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    return await controller.check()

