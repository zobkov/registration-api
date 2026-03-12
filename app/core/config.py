from functools import lru_cache

from pydantic import AnyHttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    db_user: str
    db_pass: str
    db_name: str
    db_host: str
    db_port: int

    app_name: str = "Registration API"
    api_prefix: str = "/api/v1"
    cors_origins: list[AnyHttpUrl] = [
        "https://zobkov-server.ru",
        "https://www.zobkov-server.ru",
        "https://zobkov.github.io",
    ]
    rate_limit_create_registration: str = "30/minute"

    @property
    def sqlalchemy_database_uri(self) -> str:
        return (
            f"postgresql+psycopg://{self.db_user}:{self.db_pass}@"
            f"{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: object) -> object:
        if isinstance(value, str):
            return [item.strip() for item in value.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
