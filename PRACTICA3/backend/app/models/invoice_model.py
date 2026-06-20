from datetime import date
from decimal import Decimal
from enum import StrEnum

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class InvoiceStatus(StrEnum):
    PENDING = "pending"
    PROCESSED = "processed"
    ERROR = "error"
    REJECTED = "rejected"


class Invoice(TimestampMixin, Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_number: Mapped[str | None] = mapped_column(String(100), index=True)
    invoice_date: Mapped[date | None] = mapped_column(Date)
    provider_id: Mapped[int | None] = mapped_column(
        ForeignKey("providers.id", ondelete="SET NULL")
    )
    detected_provider_name: Mapped[str | None] = mapped_column(String(160))
    detected_nit: Mapped[str | None] = mapped_column(String(30))
    subtotal: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    taxes: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    ocr_text: Mapped[str | None] = mapped_column(Text)
    status: Mapped[InvoiceStatus] = mapped_column(
        Enum(InvoiceStatus, native_enum=False),
        default=InvoiceStatus.PENDING,
        index=True,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        index=True,
        nullable=False,
    )
    uploaded_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )

    provider: Mapped["Provider | None"] = relationship(back_populates="invoices")
    uploaded_by: Mapped["User | None"] = relationship(back_populates="invoices")
    processing_logs: Mapped[list["ProcessingLog"]] = relationship(
        back_populates="invoice",
        cascade="all, delete-orphan",
    )
