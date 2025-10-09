from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from tickets.crud import create_ticket_crud, get_ticket_by_id, update_ticket_crud, delete_ticket_crud
from tickets.models import Ticket
from tickets.schemas import TicketCreate, TicketUpdate


async def create_ticket_service(ticket_data: TicketCreate, user_id: int, db: AsyncSession) -> Ticket:
    """Бизнес-логика создания ticket"""
    # бизнес-логика: проверка прав, ограничения
    if len(ticket_data.title) > 100:
        raise ValueError("Title too long")

    ticket = await create_ticket_crud(ticket_data, user_id=user_id, db=db)

    # дополнительная логика
    # send_email(ticket)
    return ticket


async def get_tickets_service(user_id: int, db: AsyncSession) -> list[Ticket]:
    """Бизнес-логика получения tickets пользователя"""
    tickets = await get_tickets_service(user_id=user_id, db=db)
    return tickets


async def update_ticket_service(ticket_update: TicketUpdate, user_id: int, db: AsyncSession) -> Ticket:
    """Бизнес-логика обновления ticket"""
    ticket = await get_ticket_by_id(db, ticket_update.id)
    if not ticket:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")

    if ticket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

    await update_ticket_crud(ticket_update, db=db)
    return ticket


async def delete_ticket_service(ticket_id: int, user_id: int, db: AsyncSession) -> bool:
    """Бизнес-логика удаления ticket"""
    ticket = await get_ticket_by_id(db, ticket_id)
    if ticket.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")
    await delete_ticket_crud(ticket_id, db=db)
    return True
