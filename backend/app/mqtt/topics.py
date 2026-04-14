"""MQTT topic definitions for the CGM platform.

All topic patterns used by the backend consumer are declared here.
No MQTT topic string should be hardcoded elsewhere.
"""

# ── Glucose readings from CGM sensors ─────────────
# Published by edge simulators on: cgm/glucose/{patient_id}
# Backend subscribes with single-level wildcard to catch all patients.
GLUCOSE_TOPIC = "cgm/glucose/+"

# ── Device status heartbeats (future) ─────────────
STATUS_TOPIC = "cgm/status/+"

# ── All subscriptions for the backend consumer ────
ALL_SUBSCRIPTIONS = [
    GLUCOSE_TOPIC,
    # STATUS_TOPIC,  # uncomment when status handler is ready
]
