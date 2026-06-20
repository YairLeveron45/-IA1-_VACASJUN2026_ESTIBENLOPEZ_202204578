from app.schemas.system_settings_schema import SystemSettingsResponse
from app.services.system_settings_service import SystemSettingsService


class SystemSettingsController:
    def __init__(self, service: SystemSettingsService | None = None) -> None:
        self.service = service or SystemSettingsService()

    def get(self) -> SystemSettingsResponse:
        return self.service.get_safe_settings()
