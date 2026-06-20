from __future__ import annotations

from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.invoice_model import Invoice, InvoiceStatus
from app.models.processing_log_model import ProcessingLog


class InvoiceRepository:
    """Encapsula las consultas y transacciones de facturas."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def list(
        self,
        offset: int,
        limit: int,
        status: InvoiceStatus | None = None,
        provider_id: int | None = None,
        search: str | None = None,
    ) -> tuple[list[Invoice], int]:
        """Consulta facturas activas con filtros y devuelve el total."""
        filters = [Invoice.is_deleted.is_(False)]
        if status is not None:
            filters.append(Invoice.status == status)
        if provider_id is not None:
            filters.append(Invoice.provider_id == provider_id)
        if search:
            term = f"%{search.strip()}%"
            filters.append(
                or_(
                    Invoice.file_name.ilike(term),
                    Invoice.invoice_number.ilike(term),
                    Invoice.detected_provider_name.ilike(term),
                    Invoice.detected_nit.ilike(term),
                )
            )

        items_query = (
            select(Invoice)
            .where(*filters)
            .order_by(Invoice.created_at.desc(), Invoice.id.desc())
            .offset(offset)
            .limit(limit)
        )
        count_query = select(func.count()).select_from(Invoice).where(*filters)

        items_result = await self.session.execute(items_query)
        total_result = await self.session.execute(count_query)
        return list(items_result.scalars().all()), total_result.scalar_one()

    async def get_by_id(self, invoice_id: int) -> Invoice | None:
        """Busca una factura no eliminada por su identificador."""
        result = await self.session.execute(
            select(Invoice).where(
                Invoice.id == invoice_id,
                Invoice.is_deleted.is_(False),
            )
        )
        return result.scalar_one_or_none()

    async def stats(self) -> dict[str, int]:
        """Agrupa las facturas por estado para el panel administrativo."""
        result = await self.session.execute(
            select(Invoice.status, func.count())
            .where(Invoice.is_deleted.is_(False))
            .group_by(Invoice.status)
        )
        counts = {status.value: count for status, count in result.all()}
        return {
            "total": sum(counts.values()),
            "pending": counts.get(InvoiceStatus.PENDING.value, 0),
            "processed": counts.get(InvoiceStatus.PROCESSED.value, 0),
            "error": counts.get(InvoiceStatus.ERROR.value, 0),
            "rejected": counts.get(InvoiceStatus.REJECTED.value, 0),
        }

    async def create_with_log(
        self,
        invoice: Invoice,
        log: ProcessingLog,
    ) -> Invoice:
        """Crea factura y bitácora dentro de una sola transacción."""
        try:
            self.session.add(invoice)
            await self.session.flush()
            log.invoice_id = invoice.id
            self.session.add(log)
            await self.session.commit()
            await self.session.refresh(invoice)
            return invoice
        except Exception:
            # El rollback evita guardar una factura sin su evento de auditoría.
            await self.session.rollback()
            raise

    async def update_with_log(
        self,
        invoice: Invoice,
        log: ProcessingLog,
    ) -> Invoice:
        """Actualiza una factura junto con un único evento de bitácora."""
        return await self.update_with_logs(invoice, [log])

    async def update_with_logs(
        self,
        invoice: Invoice,
        logs: list[ProcessingLog],
    ) -> Invoice:
        """Confirma una factura y varios eventos de forma atómica."""
        try:
            self.session.add_all(logs)
            await self.session.commit()
            await self.session.refresh(invoice)
            return invoice
        except Exception:
            # Revierte todos los cambios si falla cualquiera de los registros.
            await self.session.rollback()
            raise

    async def add_log(self, log: ProcessingLog) -> ProcessingLog:
        """Agrega un evento independiente a la bitácora."""
        self.session.add(log)
        await self.session.commit()
        await self.session.refresh(log)
        return log
