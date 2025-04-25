"""Модуль для конфигурации логирования и метрик."""

import aioprometheus
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogConfig(BaseSettings):
    """Класс для конфгурации логирования."""

    model_config = SettingsConfigDict(env_prefix='LOG_', env_file='.env', extra='ignore')
    level: str = 'INFO'
    formatter: str | None = 'json'


class Metrics:
    """
    Класс для конфгурации prometheus метрик.

    Атрибуты:
        - `http_requests_latency`: Гистограмма для измерения латентности
            HTTP-запросов с заранее определенными интервалами.
    """

    http_requests_latency = aioprometheus.Histogram(
        'http_requests_latency',
        'Гистограмма на все случаи жизни',
        buckets=[50, 100, 300, 500, 1000, 2000, 5000, 10000],
    )

    @staticmethod
    def render() -> tuple[bytes, dict]:  # noqa: WPS605
        """
        Рендеринг текущих метрик, собранных Prometheus.

        Returns:
            tuple[bytes, dict[str, str]]: Кортеж, содержащий:
                                        - Метрики в виде байтовой строки.
                                        - Словарь заголовков для ответа.
        """
        return aioprometheus.render(
            aioprometheus.REGISTRY,
            [],
        )
