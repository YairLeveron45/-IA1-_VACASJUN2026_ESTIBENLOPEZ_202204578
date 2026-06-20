from datetime import datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.processing_log_model import ProcessingLog


class ProcessingLogRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        offset: int,
        limit: int,
        invoice_id: int | None = None,
        user_id: int | None = None,
        action: str | None = None,
        status: str | None = None,
        date_from: datetime | None = None,
        date_to: datetime | None = None,
    ) -> tuple[list[ProcessingLog], int]:
        filters = []
        if invoice_id is not None:
            filters.append(ProcessingLog.invoice_id == invoice_id)
        if user_id is not None:
            filters.append(ProcessingLog.user_id == user_id)
        if action:
            filters.append(ProcessingLog.action == action)
        if status:
            filters.append(ProcessingLog.status == status)
        if date_from:
            filters.append(ProcessingLog.created_at >= date_from)
        if date_to:
            filters.append(ProcessingLog.created_at <= date_to)

        items_query = (
            select(ProcessingLog)
            .where(*filters)
            .order_by(
                ProcessingLog.created_at.desc(),
                ProcessingLog.id.desc(),
            )
            .offset(offset)
            .limit(limit)
        )
        count_query = (
            select(func.count()).select_from(ProcessingLog).where(*filters)
        )
        items_result = await self.session.execute(items_query)
        count_result = await self.session.execute(count_query)
        return list(items_result.scalars().all()), count_result.scalar_one()

    async def get_by_id(self, log_id: int) -> ProcessingLog | None:
        return await self.session.get(ProcessingLog, log_id)

    async def create(self, log: ProcessingLog) -> ProcessingLog:
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log
