from datetime import datetime, UTC

import enum
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship


from core.base import MyBaseModel

if TYPE_CHECKING:
    from users.models import User



class TicketStatus(str, enum.Enum):
    """Список статусов для Ticket"""
    open = "open"
    in_progress = "in_progress"
    closed = "closed"


class Ticket(MyBaseModel):
    """Модель Ticket"""
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        Enum(TicketStatus, name="ticket_status"),
        default=TicketStatus.open,
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now(UTC), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)

    user: Mapped["User"] = relationship(
        argument="User",
        back_populates="tickets",
        lazy="joined")
