"""Dashboard configuration."""

import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "30"))
APP_TITLE = "GlucoWatch"
APP_SUBTITLE = "Continuous Glucose Monitoring Platform"

# Display names for demo patients (presentation layer only)
PATIENT_PROFILES = {
    "PAT-001": {"name": "Ahmed Tounli", "age": 34, "type": "Type 2"},
    "PAT-002": {"name": "Youssef Amrani", "age": 52, "type": "Type 2"},
    "PAT-003": {"name": "Fatima Zahra", "age": 28, "type": "Type 1"},
}


def get_patient_display_name(patient_id: str) -> str:
    profile = PATIENT_PROFILES.get(patient_id)
    return profile["name"] if profile else patient_id


def get_patient_profile(patient_id: str) -> dict:
    return PATIENT_PROFILES.get(patient_id, {"name": patient_id, "age": "—", "type": "—"})
