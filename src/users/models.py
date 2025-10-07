from datetime import datetime, UTC
from typing import TYPE_CHECKING

from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.base import MyBaseModel

if TYPE_CHECKING:
    from tickets.models import Ticket


class User(MyBaseModel):
    """Модель User"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC))

    tickets: Mapped[list["Ticket"]] = relationship(
        argument="Ticket",
        back_populates="user",
        passive_deletes=True,
        single_parent=True,
        cascade="all, delete-orphan",
        lazy="selectin",
    )
