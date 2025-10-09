from datetime import datetime

from pydantic import BaseModel, Field, ConfigDict, field_validator

from tickets.models import TicketStatus


class TicketCreate(BaseModel):
    title: str = Field(..., max_length=200, description="Заголовок тикета")
    description: str = Field(..., description="Описание проблемы")


class TicketResponse(BaseModel):
    id: int = Field(gt=0, description="ID тикета")
    user_id: int = Field(gt=0, description="ID владельца")
    title: str = Field(..., max_length=200, description="Заголовок тикета")
    description: str = Field(..., description="Описание проблемы")
    created_at: datetime = Field(..., description="Время создания")
    updated_at: datetime | None = Field(None, description="Время обновления")

    model_config = ConfigDict(from_attributes=True)


class TicketUpdate(BaseModel):
    id: int = Field(gt=0, description="ID тикета")
    title: str | None = Field(None, max_length=200)
    description: str | None = Field(None)
    status: TicketStatus | None = Field(None, description="Статус тикета",
                                        examples=[status.value for status in TicketStatus])

    @field_validator('status')
    @classmethod
    def validate_status(cls, v):
        if v is not None and v not in TicketStatus:
            raise ValueError(f"Status must be one of: {', '.join([e.value for e in TicketStatus])}")
        return v
