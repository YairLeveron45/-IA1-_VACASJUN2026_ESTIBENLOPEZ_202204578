from fastapi import APIRouter

from app.controllers.system_settings_controller import SystemSettingsController
from app.routes.dependencies import AdminUserDependency
from app.schemas.system_settings_schema import SystemSettingsResponse


router = APIRouter(prefix="/settings", tags=["Settings"])
controller = SystemSettingsController()


@router.get("", response_model=SystemSettingsResponse)
async def get_system_settings(
    _: AdminUserDependency,
) -> SystemSettingsResponse:
    return controller.get()
