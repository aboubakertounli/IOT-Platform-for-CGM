"""Patient summary cards for the doctor dashboard."""

from __future__ import annotations

import streamlit as st

from app.config import get_patient_display_name, get_patient_profile

_STATUS_COLORS = {
    "normal": "#10B981",
    "warning": "#F59E0B",
    "critical": "#EF4444",
    "unknown": "#9CA3AF",
}

_CARD_CLASS = {
    "normal": "patient-card-normal",
    "warning": "patient-card-warning",
    "critical": "patient-card-critical",
}

_TREND_LABELS = {
    "rapid_rise": "Rising Rapidly",
    "rising": "Rising",
    "stable": "Stable",
    "falling": "Falling",
    "rapid_fall": "Falling Rapidly",
}

_SEV_PRIORITY = {"critical": 0, "warning": 1, "info": 2}


def build_patient_summaries(patients: list[dict], api_client) -> list[dict]:
    """Fetch latest data for each patient and build sorted summaries."""
    summaries = []
    for p in patients:
        pid = p["patient_id"]
        latest = api_client.get_latest_glucose(pid)
        active_alerts = api_client.get_active_alerts(pid)
        classification = latest.get("classification", "unknown") if latest else "unknown"

        worst_sev = "info"
        if active_alerts:
            for a in active_alerts:
                s = a.get("severity", "info")
                if _SEV_PRIORITY.get(s, 3) < _SEV_PRIORITY.get(worst_sev, 3):
                    worst_sev = s

        summaries.append({
            "patient_id": pid,
            "latest": latest,
            "active_alerts": active_alerts,
            "classification": classification,
            "worst_severity": worst_sev,
            "n_alerts": len(active_alerts) if active_alerts else 0,
            "priority": _SEV_PRIORITY.get(worst_sev, 3),
        })

    summaries.sort(key=lambda s: (s["priority"], -s["n_alerts"]))
    return summaries


def render_patient_card(summary: dict) -> bool:
    """Render a single patient card. Returns True if 'View' was clicked."""
    pid = summary["patient_id"]
    latest = summary["latest"]
    classification = summary["classification"]
    n_alerts = summary["n_alerts"]
    profile = get_patient_profile(pid)
    name = profile["name"]
    card_class = _CARD_CLASS.get(classification, "")
    color = _STATUS_COLORS.get(classification, "#9CA3AF")

    glucose_str = f"{latest['glucose_mg_dl']:.0f} mg/dL" if latest else "No data"
    trend = latest.get("trend_direction", "stable") if latest else "stable"
    trend_label = _TREND_LABELS.get(trend, "Stable")

    badge_class = f"badge-{classification}" if classification in _STATUS_COLORS else "badge-info"
    alert_text = f"{n_alerts} active alert{'s' if n_alerts != 1 else ''}" if n_alerts > 0 else "No active alerts"

    col_card, col_btn = st.columns([5, 1])

    with col_card:
        st.markdown(
            f"""
            <div class="patient-card {card_class}">
                <div>
                    <span class="patient-card-name">{name}</span>
                    <span class="patient-card-id" style="margin-left:0.5rem;">{pid}</span>
                </div>
                <div class="patient-card-glucose" style="color:{color};">{glucose_str}</div>
                <div class="patient-card-meta">
                    <span class="badge {badge_class}">{classification.upper()}</span>
                    &nbsp; {trend_label} &nbsp;&middot;&nbsp; {alert_text}
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        return st.button("View", key=f"view_{pid}", use_container_width=True)
