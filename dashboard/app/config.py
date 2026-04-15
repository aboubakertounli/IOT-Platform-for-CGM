"""Dashboard configuration — environment-based settings."""

import os


BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
REFRESH_INTERVAL_SECONDS = int(os.getenv("REFRESH_INTERVAL_SECONDS", "30"))
APP_TITLE = "CGM IoT Platform"
