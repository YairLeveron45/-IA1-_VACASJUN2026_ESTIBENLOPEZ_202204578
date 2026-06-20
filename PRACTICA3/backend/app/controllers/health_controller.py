from app.schemas.health_schema import HealthResponse
from app.services.health_service import HealthService


class HealthController:
    def __init__(self, service: HealthService | None = None) -> None:
        self.service = service or HealthService()

    async def check(self) -> HealthResponse:
        return self.service.get_status()

