import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from utils import fake_create_user, fake_create_ticket
from tickets.models import Ticket, TicketStatus
from tickets.schemas import TicketCreate, TicketUpdate
from users.models import User
from users.schemas import UserRegister


@pytest.mark.asyncio
async def test_register_user_success(mocker, db_session: AsyncSession):
    """Успешная регистрация нового пользователя"""
    from users.service import register_user
    mocker.patch("users.service.get_user_by_email", return_value=None)
    mocker.patch("users.service.get_user_by_username", return_value=None)
    mock_create_user = mocker.patch("users.service.create_user", autospec=True, side_effect=fake_create_user)

    user_data = UserRegister(username="new_user", email="new_user@example.com", password="password")
    user = await register_user(user_data, db_session)

    assert isinstance(user, User)
    assert user.username == "new_user"
    assert user.email == "new_user@example.com"
    mock_create_user.assert_awaited_once()


@pytest.mark.asyncio
async def test_register_user_conflict_email(mocker, db_session: AsyncSession):
    """Попытка зарегистрировать пользователя с уже существующим email"""
    from users.service import register_user
    mocker.patch("users.service.get_user_by_email",
                 return_value=User(id=1, username="other", email="test@example.com", hashed_password="hash"))
    user_data = UserRegister(username="new_user", email="test@example.com", password="password")

    with pytest.raises(HTTPException) as exc:
        await register_user(user_data, db_session)
    assert exc.value.status_code == 409
    assert "Email already registered" in exc.value.detail


@pytest.mark.asyncio
async def test_register_user_conflict_username(mocker, db_session: AsyncSession):
    """Попытка зарегистрировать пользователя с уже существующим username"""
    from users.service import register_user
    mocker.patch("users.service.get_user_by_email", return_value=None)
    mocker.patch("users.service.get_user_by_username",
                 return_value=User(id=1, username="existing_user", email="other@example.com", hashed_password="hash"))

    user_data = UserRegister(username="existing_user", email="new@example.com", password="password")

    with pytest.raises(HTTPException) as exc:
        await register_user(user_data, db_session)
    assert exc.value.status_code == 409
    assert "Username already registered" in exc.value.detail


# ------------------- Тикеты -------------------

@pytest.mark.asyncio
async def test_create_ticket_success(mocker, db_session: AsyncSession):
    """Успешное создание тикета"""
    from tickets.service import create_ticket_service
    user_id = 1
    ticket_data = TicketCreate(title="Test Ticket", description="Description")
    mock_create_crud = mocker.patch("tickets.service.create_ticket_crud", side_effect=fake_create_ticket)

    ticket = await create_ticket_service(ticket_data, user_id, db_session)
    assert isinstance(ticket, Ticket)
    assert ticket.title == "Test Ticket"
    mock_create_crud.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_ticket_long_title(mocker, db_session: AsyncSession):
    """Попытка создать тикет с длинным заголовком"""
    from tickets.service import create_ticket_service
    user_id = 1
    ticket_data = TicketCreate(title="x" * 101, description="Desc")

    with pytest.raises(ValueError) as exc:
        await create_ticket_service(ticket_data, user_id, db_session)
    assert "Title too long" in str(exc.value)


@pytest.mark.asyncio
async def test_update_ticket_not_found(mocker, db_session: AsyncSession):
    """Попытка обновить несуществующий тикет"""
    from tickets.service import update_ticket_service
    user_id = 1
    ticket_update = TicketUpdate(title="Updated", description="Updated")
    mocker.patch("tickets.service.get_ticket_by_id", return_value=None)

    with pytest.raises(HTTPException) as exc:
        await update_ticket_service(1, ticket_update, user_id, db_session)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_update_ticket_forbidden(mocker, db_session: AsyncSession):
    """Попытка обновить тикет другого пользователя"""
    from tickets.service import update_ticket_service
    user_id = 1
    ticket_update = TicketUpdate(title="Updated", description="Updated")
    ticket = Ticket(id=1, title="Old", description="Old", user_id=2, status=TicketStatus.open)
    mocker.patch("tickets.service.get_ticket_by_id", return_value=ticket)

    with pytest.raises(HTTPException) as exc:
        await update_ticket_service(1, ticket_update, user_id, db_session)
    assert exc.value.status_code == 403


@pytest.mark.asyncio
async def test_delete_ticket_success(mocker, db_session: AsyncSession):
    """Удаление тикета"""
    from tickets.service import delete_ticket_service
    user_id = 1
    ticket = Ticket(id=1, title="Old", description="Old", user_id=user_id, status=TicketStatus.open)
    mocker.patch("tickets.service.get_ticket_by_id", return_value=ticket)
    mock_delete = mocker.patch("tickets.service.delete_ticket_crud", autospec=True)

    response = await delete_ticket_service(ticket.id, user_id, db_session)
    assert response.is_deleted is True
    mock_delete.assert_awaited_once()
