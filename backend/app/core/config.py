"""
Centralized application configuration.
All settings loaded from environment variables.
"""

from functools import lru_cache

from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — validated from environment variables."""

    # ── Database ───────────────────────────────────
    POSTGRES_HOST: str = "postgres"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cgm_platform"
    POSTGRES_USER: str = "cgm_user"
    POSTGRES_PASSWORD: str = "changeme"
    DATABASE_URL: str = ""

    @model_validator(mode="after")
    def build_database_url(self) -> "Settings":
        if not self.DATABASE_URL:
            self.DATABASE_URL = (
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
                f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
            )
        return self

    # ── MQTT ───────────────────────────────────────
    MQTT_BROKER_HOST: str = "mosquitto"
    MQTT_BROKER_PORT: int = 1883
    MQTT_CLIENT_ID: str = "cgm-backend"
    MQTT_QOS: int = 1
    MQTT_KEEPALIVE: int = 60

    # ── Security ───────────────────────────────────
    JWT_SECRET: str = "change-me"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_MINUTES: int = 30

    # ── General ────────────────────────────────────
    ENV: str = "development"
    APP_NAME: str = "CGM IoT Platform"
    APP_VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached settings singleton."""
    return Settings()
