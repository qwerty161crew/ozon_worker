from pathlib import Path

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).parents[2]
ENV_FILE_PATH = BASE_DIR / ".env"


class PostgreSQL(BaseSettings):

    model_config = SettingsConfigDict(
        env_prefix="POSTGRESQL_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
    )
    db_name: str = "parser"
    db_user: str = "postgres"
    db_host: str = "127.0.0.1"
    db_port: int = 5431
    db_password: str = "1917"
    pool_size: int = 20
    debug: bool = True

    @property
    def db_url(self):

        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class RabbitmqSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="RABBITMQ_",
        env_file=str(ENV_FILE_PATH),
        env_file_encoding="utf-8",
    )
    host: str = "localhost"
    port: int = 5672
    user: str = "guest"
    password: str = "guest"

    @property
    def db_url(self):
        return f"amqp://{self.user}:{self.password}@{self.host}:{self.port}/"


class Config(BaseSettings):
    postgres: PostgreSQL
    rabbit_mq: RabbitmqSettings
    debug: bool = True

    @classmethod
    def create(cls) -> "Config":
        return cls(postgres=PostgreSQL(), rabbit_mq=RabbitmqSettings())
