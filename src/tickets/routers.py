from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated

from auth.deps import get_user_by_token
from core.deps import get_db_session
from users.models import User
from .schemas import TicketUpdate, TicketCreate, TicketResponse
from .crud import get_tickets_crud
from .service import update_ticket_service, create_ticket_service, delete_ticket_service

ticket_router = APIRouter()


@ticket_router.post("/", response_model=TicketResponse)
async def create_ticket_endpoint(ticket: TicketCreate,
                                 user: Annotated[User, Depends(get_user_by_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> TicketResponse:
    ticket = await create_ticket_service(ticket_data=ticket, user_id=user.id, db=db)
    return TicketResponse.model_validate(ticket)


@ticket_router.get("/", response_model=list[TicketResponse])
async def get_tickets_endpoint(user: Annotated[User, Depends(get_user_by_token)],
                               db: Annotated[AsyncSession, Depends(get_db_session)]) -> list[TicketResponse]:
    tickets = await get_tickets_crud(user_id=user.id, db=db)
    return [TicketResponse.model_validate(ticket) for ticket in tickets]


@ticket_router.put("/", response_model=TicketResponse)
async def update_ticket_endpoint(ticket_update: TicketUpdate,
                                 user: Annotated[User, Depends(get_user_by_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> TicketResponse:
    ticket = await update_ticket_service(ticket_update=ticket_update, user_id=user.id, db=db)
    return TicketResponse.model_validate(ticket)


@ticket_router.delete("/")
async def delete_ticket_endpoint(ticket_id: int, user: Annotated[User, Depends(get_user_by_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> bool:
    return await delete_ticket_service(ticket_id=ticket_id, user_id=user.id, db=db)