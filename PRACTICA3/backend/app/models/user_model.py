from enum import StrEnum

from sqlalchemy import Boolean, Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin


class UserRole(StrEnum):
    ADMIN = "admin"
    OPERATOR = "operator"


class User(TimestampMixin, Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, native_enum=False),
        default=UserRole.OPERATOR,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    invoices: Mapped[list["Invoice"]] = relationship(back_populates="uploaded_by")
    processing_logs: Mapped[list["ProcessingLog"]] = relationship(
        back_populates="user"
    )
    reports: Mapped[list["Report"]] = relationship(back_populates="generated_by")
