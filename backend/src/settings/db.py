"""Модуль конфигурации подключения к базе данных с использованием asyncpg и SQLAlchemy."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AsyncpgSqlaConfig(BaseSettings):
    """Класс для конфигурации подключения к базе данных с использованием asyncpg и SQLAlchemy."""

    model_config = SettingsConfigDict(
        env_prefix="ASYNCPG_SQLA_", env_file=".env", extra="ignore"
    )

    connection_string: str = ""
    connection_timeout: int = 20
    min_pool_size: int = 1
    max_pool_size: int = 5
