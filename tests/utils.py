async def fake_create_user(user_create, db):
    from users.models import User
    user = User(username=user_create.username, email=user_create.email, hashed_password=user_create.hashed_password)
    db.add(user)      # Теперь объект привязан к сессии
    return user

async def fake_create_ticket(ticket_data, user_id, db):
    from tickets.models import Ticket, TicketStatus
    ticket = Ticket(title=ticket_data.title, description=ticket_data.description, user_id=user_id, status=TicketStatus.open)
    db.add(ticket)
    return ticket