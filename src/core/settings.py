from pathlib import Path

from pydantic import Field, SecretStr, RedisDsn
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
    HOST: str = Field(alias="MYSQL_HOST", default="localhost")
    PORT: int = Field(alias="MYSQL_PORT", default=3306)
    USER: str = Field(alias="MYSQL_USER", default="bd_user")
    PASS: SecretStr = Field(alias="MYSQL_PASS", default="bd_pass")
    NAME: str = Field(alias="MYSQL_NAME", default="bd_name")

    @property
    def async_url(self) -> str:
        """Получение ссылки для асинхронной работы с MySQL"""
        return f"mysql+aiomysql://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"

    @property
    def sync_url(self) -> str:
        """Получение ссылки для синхронной работы с MySQL"""
        return f"mysql+pymysql://{self.USER}:{self.PASS.get_secret_value()}@{self.HOST}:{self.PORT}/{self.NAME}"


class RedisSettings(MyBaseSettings):
    """Конфиг Redis"""
    REDIS_URL: RedisDsn = Field(
        default="redis://redis:6379/0",
        description="Redis connection URL",
    )

    @property
    def sync_url(self) -> str:
        """Получение ссылки для синхронной работы с Redis"""
        return str(self.REDIS_URL)

class AuthSettings(MyBaseSettings):
    SECRET_KEY: SecretStr = Field(alias="SECRET_KEY", default=None)
    JWT_ALG: str = Field(alias="JWT_ALG", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(alias="ACCESS_TOKEN_EXPIRE_MINUTES", default=30)

class Settings(MyBaseSettings):
    """Конфиг всего приложения (общий конфиг)"""
    database: MySQLSettings = MySQLSettings()
    auth: AuthSettings = AuthSettings()

    DEBUG: bool = Field(alias="DEBUG", default=False)
    ENVIRONMENT: str = Field(alias="ENVIRONMENT", default="development")


settings = Settings()
