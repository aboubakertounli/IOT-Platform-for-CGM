"""Doctor — alerts center (all patients)."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.components.alerts_list import render_alert_cards


def render() -> None:
    st.markdown(
        "<h2 style='margin-bottom:0.25rem;'>Alerts Center</h2>"
        "<div class='text-muted mb-2'>All alerts across monitored patients</div>",
        unsafe_allow_html=True,
    )

    alerts = api_client.list_alerts(limit=100)
    if alerts is None:
        st.error("Unable to fetch alerts from the backend.")
        return

    if not alerts:
        st.markdown(
            "<div class='kpi-card text-center' style='padding:2rem;'>"
            "<div style='font-size:2rem;'>&#10003;</div>"
            "<div style='color:#10B981; font-weight:600; font-size:1.1rem;'>All clear</div>"
            "<div class='text-muted'>No alerts recorded across all patients</div>"
            "</div>",
            unsafe_allow_html=True,
        )
        return

    # Summary
    active = [a for a in alerts if a.get("status") == "active"]
    critical = [a for a in active if a.get("severity") == "critical"]
    warning = [a for a in active if a.get("severity") == "warning"]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Total Alerts", len(alerts))
    with c2:
        st.metric("Active", len(active))
    with c3:
        st.metric("Critical", len(critical))
    with c4:
        st.metric("Warning", len(warning))

    # Active alerts first
    if active:
        st.markdown(
            f'<div class="section-header">Active Alerts ({len(active)})</div>',
            unsafe_allow_html=True,
        )
        render_alert_cards(active, show_patient=True, allow_ack=True, key_prefix="doc_alert_active")

    # All alerts
    st.markdown('<div class="section-header">All Alerts</div>', unsafe_allow_html=True)
    render_alert_cards(alerts, show_patient=True, key_prefix="doc_alert_all")
