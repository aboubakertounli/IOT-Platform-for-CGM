"""
CGM IoT Platform — FastAPI Application Entry Point.

Phase 1: Infrastructure foundation.
Phase 3: MQTT consumer integration.
Phase 4: PostgreSQL persistence.
Phase 5: REST API for data consultation.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.db.database import init_db, close_db
from app.api.health import router as health_router
from app.api.routers.patients import router as patients_router
from app.api.routers.glucose import router as glucose_router
from app.api.routers.devices import router as devices_router
from app.mqtt.client import MqttConsumer

import app.models  # noqa: F401 — register ORM models with Base.metadata

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ── Lifespan (startup / shutdown) ──────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    # ── Startup ────────────────────────────────────
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Environment: %s", settings.ENV)
    logger.info("MQTT Broker: %s:%d", settings.MQTT_BROKER_HOST, settings.MQTT_BROKER_PORT)

    # Database
    await init_db()

    # MQTT consumer
    mqtt_consumer = MqttConsumer(
        host=settings.MQTT_BROKER_HOST,
        port=settings.MQTT_BROKER_PORT,
        qos=settings.MQTT_QOS,
        client_id=settings.MQTT_CLIENT_ID,
        keepalive=settings.MQTT_KEEPALIVE,
    )
    mqtt_consumer.start()

    yield

    # ── Shutdown ───────────────────────────────────
    mqtt_consumer.stop()
    await close_db()
    logger.info("Application shutdown complete")


# ── Application factory ────────────────────────────
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Plateforme IoT de surveillance continue du glucose",
    lifespan=lifespan,
)

# ── Middleware ─────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ────────────────────────────────────────
app.include_router(health_router)
app.include_router(patients_router)
app.include_router(glucose_router)
app.include_router(devices_router)


# ── Root endpoint ──────────────────────────────────
@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
    }
