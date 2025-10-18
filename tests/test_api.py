import pytest
from conftest import client, mock_rabbitmq, mock_redis

@pytest.mark.asyncio
async def test_user_register(client, mock_redis, mock_rabbitmq):
    """
    Проверка регистрации пользователя
    """
    from users.schemas import UserRegister

    user_data = UserRegister(
        username="test_user",
        email="test_user@example.com",  # type: ignore
        password="test_pass",
    )

    response = await client.post(
        "/users/register",
        json=user_data.model_dump()
    )

    assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
    data = response.json()
    assert "id" in data, "В ответе отсутствует id пользователя"
    assert data["username"] == "test_user"

@pytest.mark.asyncio
async def test_create_ticket(client, mock_rabbitmq, mock_redis):
    """
    Проверка создания тикета
    """
    from tickets.schemas import TicketCreate

    ticket_data = TicketCreate(
        title="test_ticket",
        description="test_description",
    )

    response = await client.post(
        "/ticket/",
        json=ticket_data.model_dump()
    )

    assert response.status_code == 201, f"Ожидался статус 201, получен {response.status_code}"
    data = response.json()
    assert "id" in data, "В ответе отсутствует id тикета"
    assert data["title"] == "test_ticket"
    assert data["description"] == "test_description"

    mock_rabbitmq.publish.assert_awaited_once()

@pytest.mark.asyncio
async def test_get_tickets(client, mock_rabbitmq, mock_redis):
    """
    Проверка получения списка тикетов пользователя
    """
    from tickets.schemas import TicketCreate

    ticket_data = TicketCreate(
        title="test_ticket",
        description="test_description",
    )
    create_response = await client.post(
        "/ticket/",
        json=ticket_data.model_dump()
    )
    assert create_response.status_code == 201, f"Ошибка создания тикета: {create_response.text}"
    created_ticket = create_response.json()

    assert "id" in created_ticket
    assert created_ticket["title"] == ticket_data.title
    assert created_ticket["description"] == ticket_data.description

    get_response = await client.get("/tickets/")
    assert get_response.status_code == 200, f"Ошибка получения тикетов: {get_response.text}"
    tickets = get_response.json()

    assert isinstance(tickets, list), "Ответ должен быть списком тикетов"
    ticket = next((t for t in tickets if t["id"] == created_ticket["id"]), None)
    assert ticket is not None, "Созданный тикет не найден в списке"
    assert ticket["title"] == ticket_data.title
    assert ticket["description"] == ticket_data.description

@pytest.mark.asyncio
async def test_update_ticket(client, mock_rabbitmq, mock_redis):
    pass

