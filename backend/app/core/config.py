"""
Centralized application configuration.
All settings loaded from environment variables.
"""

from functools import lru_cache
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings — validated from environment variables."""

    # ── Database ───────────────────────────────────
    DATABASE_URL: str

    # ── MQTT ───────────────────────────────────────
    MQTT_BROKER_HOST: str = "mosquitto"
    MQTT_BROKER_PORT: int = 1883

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
