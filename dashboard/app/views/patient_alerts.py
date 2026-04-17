"""Patient alerts page — full alert history."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.auth import get_patient_id
from app.components.alerts_list import render_alert_cards


def render() -> None:
    st.markdown(
        "<h2 style='margin-bottom:0.25rem;'>My Alerts</h2>"
        "<div class='text-muted mb-2'>Your glucose alert history</div>",
        unsafe_allow_html=True,
    )

    patient_id = get_patient_id()
    if not patient_id:
        st.warning("No patient ID linked to your account.")
        return

    # Active alerts
    active = api_client.get_active_alerts(patient_id)
    if active:
        st.markdown(
            f'<div class="section-header">Active Alerts ({len(active)})</div>',
            unsafe_allow_html=True,
        )
        render_alert_cards(active, allow_ack=True, key_prefix="pat_active")
    else:
        st.success("No active alerts. Everything looks good!")

    # Full history
    st.markdown('<div class="section-header">Alert History</div>', unsafe_allow_html=True)
    all_alerts = api_client.get_alerts_for_patient(patient_id, limit=50)
    if all_alerts:
        render_alert_cards(all_alerts, key_prefix="pat_hist")
    else:
        st.info("No alerts recorded yet.")
