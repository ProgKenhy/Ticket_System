from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated, Optional

from auth.deps import get_user_id_from_token
from core.deps import get_db_session
from .models import TicketStatus
from .schemas import TicketUpdate, TicketCreate, TicketResponse, TicketDeleteResponse
from .crud import get_tickets_crud
from .service import update_ticket_service, create_ticket_service, delete_ticket_service
from redis.service import make_cache_key, get_cached_or_set

ticket_router = APIRouter()


@ticket_router.post("/", response_model=TicketResponse)
async def create_ticket_endpoint(ticket: TicketCreate,
                                 user_id: Annotated[int, Depends(get_user_id_from_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> TicketResponse:
    ticket = await create_ticket_service(ticket_data=ticket, user_id=user_id, db=db)
    return TicketResponse.model_validate(ticket)


@ticket_router.get("/", response_model=list[TicketResponse])
async def get_tickets_endpoint(user_id: Annotated[int, Depends(get_user_id_from_token)],
                               db: Annotated[AsyncSession, Depends(get_db_session)],
                               statuses: Optional[list[TicketStatus]] = Query(None)
                               ) -> list[TicketResponse]:
    key = make_cache_key("cache:ticket:list", "/ticket", user_id,
                         statuses)  # в дальнейшем можно спрятать в get_cached_or_set
    async def loader():
        return await get_tickets_crud(user_id=user_id, statuses=statuses, db=db)

    tickets = await get_cached_or_set(key, loader)
    return [TicketResponse.model_validate(ticket) for ticket in tickets]


@ticket_router.put("/", response_model=TicketResponse)
async def update_ticket_endpoint(ticket_update: TicketUpdate,
                                 user_id: Annotated[int, Depends(get_user_id_from_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> TicketResponse:
    ticket = await update_ticket_service(ticket_update=ticket_update, user_id=user_id, db=db)
    return TicketResponse.model_validate(ticket)


@ticket_router.delete("/", response_model=TicketDeleteResponse)
async def delete_ticket_endpoint(ticket_id: int, user_id: Annotated[int, Depends(get_user_id_from_token)],
                                 db: Annotated[AsyncSession, Depends(get_db_session)]) -> TicketDeleteResponse:
    return await delete_ticket_service(ticket_id=ticket_id, user_id=user_id, db=db)
