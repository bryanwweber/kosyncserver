from enum import StrEnum

from pydantic_settings import BaseSettings, SettingsConfigDict


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

    log_level: str = "INFO"

    database_path: str = "kosyncserver.db"

    def is_development(self) -> bool:
        return self.env == Environment.DEVELOPMENT

    def is_production(self) -> bool:
        return self.env == Environment.PRODUCTION


settings: Config | None = None


def get_settings() -> Config:
    global settings
    if settings is None:
        settings = Config()
    return settings
