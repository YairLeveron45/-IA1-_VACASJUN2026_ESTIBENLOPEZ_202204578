from datetime import datetime

from app.core.exceptions import ResourceNotFoundError
from app.models.processing_log_model import ProcessingLog
from app.repositories.processing_log_repository import ProcessingLogRepository


class ProcessingLogService:
    """Consulta y registra eventos de auditoría del sistema."""

    def __init__(self, repository: ProcessingLogRepository) -> None:
        self.repository = repository

    async def list(
        self,
        page: int,
        page_size: int,
        invoice_id: int | None,
        user_id: int | None,
        action: str | None,
        status: str | None,
        date_from: datetime | None,
        date_to: datetime | None,
    ) -> tuple[list[ProcessingLog], int]:
        offset = (page - 1) * page_size
        return await self.repository.list(
            offset=offset,
            limit=page_size,
            invoice_id=invoice_id,
            user_id=user_id,
            action=action,
            status=status,
            date_from=date_from,
            date_to=date_to,
        )

    async def get(self, log_id: int) -> ProcessingLog:
        """Obtiene un evento o informa que no existe."""
        log = await self.repository.get_by_id(log_id)
        if log is None:
            raise ResourceNotFoundError("Entrada de bitácora no encontrada.")
        return log

    async def record(
        self,
        *,
        action: str,
        status: str,
        user_id: int | None = None,
        invoice_id: int | None = None,
        result: str | None = None,
        error_detail: str | None = None,
    ) -> ProcessingLog:
        """Crea un evento de bitácora con sus referencias opcionales."""
        return await self.repository.create(
            ProcessingLog(
                action=action,
                status=status,
                user_id=user_id,
                invoice_id=invoice_id,
                result=result,
                error_detail=error_detail,
            )
        )
