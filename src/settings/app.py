"""Модуль для конфигурации приложения из переменных окружения и .env файла."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    """Класс для конфигурации приложения из переменных окружения и .env файла."""

    model_config = SettingsConfigDict(env_prefix='APP_', env_file='.env', extra='ignore')
    environment: str = 'localhost'
    name: str = 'web'
