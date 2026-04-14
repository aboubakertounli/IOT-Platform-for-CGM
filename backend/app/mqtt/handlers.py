"""MQTT message handlers — parse, validate, route to services."""

import json
import logging

from pydantic import ValidationError

from app.schemas.glucose import GlucoseReading
from app.services.ingestion_service import ingestion_service

logger = logging.getLogger(__name__)

# ── Topic prefix → handler mapping ────────────────

GLUCOSE_PREFIX = "cgm/glucose/"
STATUS_PREFIX = "cgm/status/"


async def dispatch(topic: str, raw_payload: bytes) -> None:
    """Route an incoming MQTT message to the appropriate handler."""
    try:
        payload = json.loads(raw_payload)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        logger.error("Invalid JSON on topic %s: %s", topic, exc)
        return

    if topic.startswith(GLUCOSE_PREFIX):
        await _handle_glucose(topic, payload)
    elif topic.startswith(STATUS_PREFIX):
        _handle_status(topic, payload)
    else:
        logger.warning("No handler for topic %s", topic)


async def _handle_glucose(topic: str, payload: dict) -> None:
    """Validate and ingest a glucose reading."""
    try:
        reading = GlucoseReading.model_validate(payload)
    except ValidationError as exc:
        logger.error("Invalid glucose payload on %s: %s", topic, exc)
        return

    await ingestion_service.ingest(reading)


def _handle_status(topic: str, payload: dict) -> None:
    """Placeholder for future device status handling."""
    logger.info("Device status received on %s: %s", topic, payload)
