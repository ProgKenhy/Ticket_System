from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent


class MyBaseSettings(BaseSettings):
    """Базовый класс конфига"""
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )


class MySQLSettings(MyBaseSettings):
    """Конфиг MySQL"""
    HOST: str = Field(alias="MYSQL_HOST", default="mysql")
    PORT: int = Field(alias="MYSQL_PORT", default=3306)
    USER: str = Field(alias="MYSQL_USER", default="bd_user")
    PASS: SecretStr = Field(alias="MYSQL_PASS", default="bd_pass")
    NAME: str = Field(alias="MYSQL_NAME", default="bd_name")

    @property
    def async_url(self):
        """Получение ссылки для асинхронной работы с MySQL"""
        if settings.ENVIRONMENT == "testing":
            return "sqlite+aiosqlite:///:memory:"
        return f"mysql+aiomysql://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def sync_url(self) -> str:
        """Получение ссылки для синхронной работы с MySQL"""
        if settings.ENVIRONMENT == "testing":
            return "sqlite+sqlite:///:memory:"
        return f"mysql+pymysql://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"


class RedisSettings(MyBaseSettings):
    """Конфиг Redis"""
    HOST: str = Field(alias="REDIS_HOST", default="redis")
    PORT: int = Field(alias="REDIS_PORT", default=6379)
    DB: int = Field(alias="REDIS_DB", default=0)
    PASSWORD: str = Field(alias="REDIS_PASSWORD", default="")

    TTL: int = Field(alias="REDIS_TTL", default=-1)
    SESSION_COOKIE: str = "session_id"
    SESSION_PREFIX: str = "session:"
    SESSION_TTL: int = 3600

    @property
    def async_url(self) -> str:
        return f"redis://{self.HOST}:{self.PORT}/{self.DB}"


class RabbitSettings(MyBaseSettings):
    """Конфиг RabbitMQ"""
    HOST: str = Field(alias="RABBIT_HOST", default="rabbitmq")
    PORT: int = Field(alias="RABBIT_PORT", default=5672)
    USER: str = Field(alias="RABBIT_USER", default="user")
    PASSWORD: SecretStr = Field(alias="RABBIT_PASSWORD", default="password")
    QUEUE_NAME: str = Field(alias="RABBIT_QUEUE", default="fastapi_queue")


class AuthSettings(MyBaseSettings):
    """Конфиг авторизации"""
    SECRET_KEY: SecretStr = Field(alias="SECRET_KEY", default=None)
    JWT_ALG: str = Field(alias="JWT_ALG", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30)


class Settings(MyBaseSettings):
    """Конфиг приложения (общий конфиг)"""
    DEBUG: bool = Field(alias="DEBUG", default=False)
    ENVIRONMENT: str = Field(alias="ENVIRONMENT", default="development")


settings = Settings()
redis_settings = RedisSettings()
auth_settings = AuthSettings()
mysql_settings = MySQLSettings()
rabbit_settings = RabbitSettings()
