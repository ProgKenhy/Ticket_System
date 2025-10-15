import pytest
from conftest import client, mock_rabbitmq, mock_redis




@pytest.mark.asyncio
async def test_create_ticket(client, mock_rabbitmq, mock_redis):
    response = await client.post(
        "/ticket/",
        json={"title": "Test title", "description": "Test description"},
    )

    assert response.status_code == 200
    mock_rabbitmq.publish.assert_awaited_once()


#
