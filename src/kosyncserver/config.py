import logging
from enum import IntEnum, StrEnum
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class LogLevel(IntEnum):
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL


class Environment(StrEnum):
    DEVELOPMENT = "development"
    PRODUCTION = "production"


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    env: Environment = Environment.DEVELOPMENT

    port: int = 8000
    host: str = "0.0.0.0"
    loop: str = "uvloop"
    reload: bool = False
    interface: str = "asgi"

    log_level: LogLevel = LogLevel.INFO

    database_path: str = "kosyncserver.db"

    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION

    @field_validator("log_level", mode="before")
    def validate_log_level(cls, v: Any) -> LogLevel:
        if not isinstance(v, str | int):
            raise ValueError("log_level must be a string or integer")
        try:
            level = int(v)
        except ValueError:
            level = v.upper()
        if isinstance(level, int):
            return LogLevel(level)
        else:
            return LogLevel[level]


settings: Config | None = None


def get_settings() -> Config:
    global settings
    if settings is None:
        settings = Config()
    return settings
