"""Centralized HTTP client for the FastAPI backend.

Every public function returns parsed JSON (dict / list) on success,
or None when the backend is unreachable / returns an error.
"""

from __future__ import annotations

import logging
from typing import Any

import requests

from app.config import BACKEND_URL

logger = logging.getLogger(__name__)

_TIMEOUT = 10  # seconds


def _get(path: str, params: dict | None = None) -> Any | None:
    """GET helper with unified error handling."""
    try:
        resp = requests.get(
            f"{BACKEND_URL}{path}",
            params=params,
            timeout=_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        logger.warning("Backend unreachable at %s", BACKEND_URL)
        return None
    except requests.HTTPError as exc:
        logger.warning("HTTP %s for %s", exc.response.status_code, path)
        return None
    except Exception as exc:
        logger.error("Unexpected error calling %s: %s", path, exc)
        return None


def _put(path: str) -> Any | None:
    """PUT helper with unified error handling."""
    try:
        resp = requests.put(f"{BACKEND_URL}{path}", timeout=_TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.ConnectionError:
        logger.warning("Backend unreachable at %s", BACKEND_URL)
        return None
    except requests.HTTPError as exc:
        logger.warning("HTTP %s for %s", exc.response.status_code, path)
        return None
    except Exception as exc:
        logger.error("Unexpected error calling %s: %s", path, exc)
        return None


# ── Health ────────────────────────────────────────────

def check_health() -> dict | None:
    return _get("/health")


def check_health_db() -> dict | None:
    return _get("/health/db")


# ── Patients ──────────────────────────────────────────

def list_patients() -> list[dict] | None:
    return _get("/api/patients")


def get_patient(patient_id: str) -> dict | None:
    return _get(f"/api/patients/{patient_id}")


# ── Glucose ───────────────────────────────────────────

def get_latest_glucose(patient_id: str) -> dict | None:
    return _get(f"/api/glucose/{patient_id}/latest")


def get_glucose_history(
    patient_id: str,
    limit: int = 100,
    offset: int = 0,
    order: str = "asc",
) -> dict | None:
    return _get(
        f"/api/glucose/{patient_id}/history",
        params={"limit": limit, "offset": offset, "order": order},
    )


def get_glucose_stats(patient_id: str) -> dict | None:
    return _get(f"/api/glucose/{patient_id}/stats")


# ── Devices ───────────────────────────────────────────

def list_devices() -> list[dict] | None:
    return _get("/api/devices")


def get_devices_for_patient(patient_id: str) -> list[dict] | None:
    return _get(f"/api/devices/patient/{patient_id}")


# ── Alerts ────────────────────────────────────────────

def list_alerts(limit: int = 100) -> list[dict] | None:
    return _get("/api/alerts", params={"limit": limit})


def get_alerts_for_patient(patient_id: str, limit: int = 100) -> list[dict] | None:
    return _get(f"/api/alerts/{patient_id}", params={"limit": limit})


def get_active_alerts(patient_id: str) -> list[dict] | None:
    return _get(f"/api/alerts/{patient_id}/active")


def acknowledge_alert(alert_id: int) -> dict | None:
    return _put(f"/api/alerts/{alert_id}/acknowledge")


# ── Analysis ──────────────────────────────────────────

def get_latest_analysis(patient_id: str) -> dict | None:
    return _get(f"/api/analysis/{patient_id}/latest")
