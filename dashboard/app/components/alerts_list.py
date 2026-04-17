"""Card-based alert display components."""

from __future__ import annotations

from datetime import datetime

import streamlit as st

from app import api_client
from app.config import get_patient_display_name

_SEV_CLASS = {"critical": "alert-card-critical", "warning": "alert-card-warning", "info": "alert-card-info"}
_SEV_LABEL_COLOR = {"critical": "#991B1B", "warning": "#92400E", "info": "#1E40AF"}


def render_alert_cards(
    alerts: list[dict],
    show_patient: bool = False,
    allow_ack: bool = False,
    key_prefix: str = "alerts",
) -> None:
    """Render alerts as styled cards."""
    if not alerts:
        st.markdown(
            "<div class='text-center text-muted mt-2'>No alerts to display.</div>",
            unsafe_allow_html=True,
        )
        return

    for i, alert in enumerate(alerts):
        sev = alert.get("severity", "info")
        card_class = _SEV_CLASS.get(sev, "alert-card-info")
        label_color = _SEV_LABEL_COLOR.get(sev, "#1E40AF")
        msg = alert.get("message", "")
        ts = alert.get("created_at", "")
        status = alert.get("status", "active")
        alert_type = alert.get("type", "").replace("_", " ").title()

        # Format timestamp
        try:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            ts_display = dt.strftime("%b %d, %H:%M")
        except (ValueError, AttributeError):
            ts_display = ts[:16] if ts else ""

        patient_line = ""
        if show_patient:
            pid = alert.get("patient_id", "")
            pname = get_patient_display_name(pid)
            patient_line = f"<span style='color:#374151; font-weight:500;'>{pname}</span> &middot; "

        status_badge = ""
        if status == "acknowledged":
            status_badge = " &middot; <span style='color:#6B7280;'>Acknowledged</span>"

        st.markdown(
            f"""
            <div class="alert-card {card_class}">
                <div>
                    <span class="alert-severity" style="color:{label_color};">{sev.upper()}</span>
                    &middot; <span style="color:#6B7280; font-size:0.8rem;">{alert_type}</span>
                    {status_badge}
                </div>
                <div class="alert-message">{patient_line}{msg}</div>
                <div class="alert-time">{ts_display}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if allow_ack and status == "active":
            if st.button("Acknowledge", key=f"{key_prefix}_ack_{alert.get('id', i)}"):
                result = api_client.acknowledge_alert(alert["id"])
                if result:
                    st.rerun()
