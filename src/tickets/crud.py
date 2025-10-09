from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from users.models import User
from .models import Ticket
from .schemas import TicketCreate, TicketUpdate


async def create_ticket_crud(ticket_data: TicketCreate, user_id: int, db: AsyncSession):
    """Добавление ticket пользователя в БД"""
    ticket = Ticket(**ticket_data.model_dump())
    ticket.user_id = user_id
    db.add(ticket)
    await db.commit()
    await db.refresh(ticket)
    return ticket


async def get_tickets_crud(user_id: int, db: AsyncSession) -> list[Ticket]:
    """Получение tickets пользователя из БД"""
    stmt = select(Ticket).where(Ticket.user_id == user_id)
    result = await db.execute(stmt)
    tickets = result.scalars().all()
    if not tickets:
        raise HTTPException(status_code=404, detail="No tickets found for this user")
    return list(tickets)


async def get_ticket_by_id(db: AsyncSession, ticket_id: int) -> Ticket | None:
    """Получение ticket по id"""
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    res = await db.execute(stmt)
    return res.scalar_one_or_none()


async def update_ticket_crud(ticket_update: TicketUpdate, db: AsyncSession) -> Ticket:
    """Обновление ticket в БД"""
    update_data = ticket_update.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(status_code=400, detail="No data to update")

    stmt = select(Ticket).where(Ticket.id == ticket_update.id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")

    for field, value in update_data.items():
        setattr(ticket, field, value)

    await db.commit()
    await db.refresh(ticket)
    return ticket


async def delete_ticket_crud(ticket_id: int, db: AsyncSession) -> bool:
    """Удаление ticket из БД"""
    stmt = select(Ticket).where(Ticket.id == ticket_id)
    result = await db.execute(stmt)
    ticket = result.scalar_one_or_none()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    delete_stmt = delete(Ticket).where(Ticket.id == ticket_id)
    await db.execute(delete_stmt)
    await db.commit()
    return True
