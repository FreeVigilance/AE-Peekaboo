"""
Модуль конфигурации приложения и логирования.

Содержит класс Settings, который содержит настройки для
конфигурации приложения, базы данных, ARQ, логирования и метрик.
"""

import sys
from logging import Formatter, LogRecord, config
from typing import Any

import ujson
from pydantic_settings import BaseSettings

from .app import AppConfig
from .db import AsyncpgSqlaConfig
from .log import LogConfig, Metrics

LEVEL = 'level'
CONSOLE = 'console'


class Settings(BaseSettings):
    """
    Класс для загрузки и хранения настроек приложения.

    Инкапсулирует настройки для приложения, логирования, базы данных, ARQ и метрик.
    """

    app: AppConfig = AppConfig()
    log: LogConfig = LogConfig()
    metrics: Metrics = Metrics()
    db: AsyncpgSqlaConfig = AsyncpgSqlaConfig()

settings = Settings()


class JSONFormatter(Formatter):
    """Кастомный форматтер для логирования в JSON-формате."""

    def __init__(
        self,
        *args: Any,
        serialization_params: dict | None = None,
        extra: dict | None = None,
        **kwargs: Any,
    ):
        super().__init__(*args, **kwargs)
        self._serialization_params = serialization_params.copy() if serialization_params else {}
        self._extra = extra.copy() if extra else {}

    def format(self, record: LogRecord) -> str:
        """
        Форматирует запись лога в JSON-строку.

        Args:
            record (LogRecord): Объект записи лога.

        Returns:
            str: Строка JSON, представляющая запись лога.
        """
        log_data = {
            'time': record.created,
            'name': record.name,
            'level': record.levelname,
            'msg': record.getMessage(),
            'func': f'{record.module}.{record.funcName}:{record.lineno}',
        }

        if record.exc_info:
            exc_info = self.formatException(record.exc_info)
            log_data['exc_info'] = exc_info
        log_data.update(self._extra)

        return ujson.dumps(log_data, **self._serialization_params)


CONFIG_DICT: dict = dict(  # noqa: C408
    version=1,
    disable_existing_loggers=False,
    loggers={
        '': {
            LEVEL: settings.log.level,
            'handlers': [CONSOLE],
        },
        'uvicorn': {
            LEVEL: settings.log.level,
            'handlers': [CONSOLE],
        },
        'root': {
            LEVEL: settings.log.level,
            'handlers': [CONSOLE],
            'propagate': False,
        },
    },
    handlers={
        CONSOLE: {
            'class': 'logging.StreamHandler',
            'formatter': settings.log.formatter,
            'stream': sys.stdout,
        },
    },
    formatters={
        'json': {
            '()': JSONFormatter,
            'serialization_params': {'ensure_ascii': False},
        },
    },
)

config.dictConfig(CONFIG_DICT)
