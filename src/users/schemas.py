from pydantic import BaseModel, Field, EmailStr


class UserCreate(BaseModel):
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Почта пользователя")
    hashed_password: str


class UserRegister(BaseModel):
    username: str = Field(description="Имя пользователя")
    email: EmailStr = Field(description="Почта пользователя")
    password: str


class UserResponse(BaseModel):
    id: int = Field(gt=0, description="ID пользователя")
    username: str
    email: EmailStr


    class Config:
        from_attributes = True