from __future__ import annotations

from datetime import date, datetime, time

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.processing_log_model import ProcessingLog
from app.models.report_model import Report


class ReportRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        offset: int,
        limit: int,
    ) -> tuple[list[Report], int]:
        items_result = await self.session.execute(
            select(Report)
            .order_by(Report.created_at.desc(), Report.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_result = await self.session.execute(
            select(func.count()).select_from(Report)
        )
        return list(items_result.scalars().all()), count_result.scalar_one()

    async def get_by_id(self, report_id: int) -> Report | None:
        return await self.session.get(Report, report_id)

    async def get_invoices(
        self,
        date_from: date | None,
        date_to: date | None,
        provider_id: int | None,
        status: InvoiceStatus | None,
    ) -> list[Invoice]:
        filters = [Invoice.is_deleted.is_(False)]
        if date_from:
            filters.append(
                Invoice.created_at >= datetime.combine(date_from, time.min)
            )
        if date_to:
            filters.append(
                Invoice.created_at <= datetime.combine(date_to, time.max)
            )
        if provider_id:
            filters.append(Invoice.provider_id == provider_id)
        if status:
            filters.append(Invoice.status == status)

        result = await self.session.execute(
            select(Invoice)
            .where(*filters)
            .order_by(Invoice.created_at, Invoice.id)
        )
        return list(result.scalars().all())

    async def create_with_log(
        self,
        report: Report,
        log: ProcessingLog,
    ) -> Report:
        try:
            self.session.add(report)
            await self.session.flush()
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(report)
            return report
        except Exception:
            await self.session.rollback()
            raise

    async def create_log(self, log: ProcessingLog) -> ProcessingLog:
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log
