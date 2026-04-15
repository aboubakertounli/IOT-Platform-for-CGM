"""Alert display components."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from app import api_client

_SEVERITY_EMOJI = {
    "critical": "🔴",
    "warning": "🟡",
    "info": "🔵",
}


def render_alerts_table(alerts: list[dict], show_patient: bool = False) -> None:
    """Render alerts as a styled dataframe with acknowledge action."""
    if not alerts:
        st.info("No alerts to display.")
        return

    df = pd.DataFrame(alerts)
    df["created_at"] = pd.to_datetime(df["created_at"]).dt.strftime("%Y-%m-%d %H:%M:%S")

    # Add severity indicator
    df["sev"] = df["severity"].map(lambda s: _SEVERITY_EMOJI.get(s, "") + " " + s.upper())

    columns = ["id", "sev", "type", "message", "status", "created_at"]
    labels = {
        "id": "ID",
        "sev": "Severity",
        "type": "Type",
        "message": "Message",
        "status": "Status",
        "created_at": "Created",
    }
    if show_patient:
        columns.insert(1, "patient_id")
        labels["patient_id"] = "Patient"

    display_df = df[columns].rename(columns=labels)
    st.dataframe(display_df, use_container_width=True, hide_index=True)

    # Acknowledge action for active alerts
    active = [a for a in alerts if a.get("status") == "active"]
    if active:
        col1, col2 = st.columns([3, 1])
        with col1:
            selected_id = st.selectbox(
                "Select alert to acknowledge",
                options=[a["id"] for a in active],
                format_func=lambda x: f"Alert #{x}",
                key="ack_select",
            )
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("Acknowledge", key="ack_btn"):
                result = api_client.acknowledge_alert(selected_id)
                if result:
                    st.success(f"Alert #{selected_id} acknowledged.")
                    st.rerun()
                else:
                    st.error("Failed to acknowledge alert.")
