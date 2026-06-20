from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class ProcessingLog(TimestampMixin, Base):
    __tablename__ = "processing_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    invoice_id: Mapped[int | None] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"),
        index=True,
    )
    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL")
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(String(30), nullable=False)
    result: Mapped[str | None] = mapped_column(Text)
    error_detail: Mapped[str | None] = mapped_column(Text)

    invoice: Mapped["Invoice | None"] = relationship(
        back_populates="processing_logs"
    )
    user: Mapped["User | None"] = relationship(back_populates="processing_logs")
