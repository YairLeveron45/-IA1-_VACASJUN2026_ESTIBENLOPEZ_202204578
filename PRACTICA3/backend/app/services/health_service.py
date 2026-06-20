from app.core.config import settings
from app.schemas.health_schema import HealthResponse


class HealthService:
    def get_status(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            application=settings.app_name,
            environment=settings.app_env,
        )

