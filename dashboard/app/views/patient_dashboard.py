"""Patient dashboard — personal glucose monitoring view."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.auth import get_name, get_patient_id
from app.components.metrics_cards import render_glucose_hero, render_stats_row
from app.components.charts import render_glucose_chart
from app.components.alerts_list import render_alert_cards


def render() -> None:
    patient_id = get_patient_id()
    name = get_name()

    st.markdown(
        f"<h2 style='margin-bottom:0.25rem;'>Welcome back, {name.split()[0]}</h2>"
        f"<div class='text-muted mb-2'>Your glucose monitoring dashboard</div>",
        unsafe_allow_html=True,
    )

    if not patient_id:
        st.warning("No patient ID linked to your account. Please contact support.")
        return

    # ── Current glucose ──────────────────────────────
    latest = api_client.get_latest_glucose(patient_id)
    if latest is None:
        st.info("Waiting for your first glucose reading from the sensor...")
        _render_device_status(patient_id)
        return

    render_glucose_hero(latest)

    # ── Statistics ────────────────────────────────────
    stats = api_client.get_glucose_stats(patient_id)
    if stats and stats.get("count", 0) > 0:
        st.markdown('<div class="section-header">Statistics</div>', unsafe_allow_html=True)
        render_stats_row(stats)

    # ── 24h Trend chart ──────────────────────────────
    st.markdown('<div class="section-header">Glucose Trend</div>', unsafe_allow_html=True)
    history = api_client.get_glucose_history(patient_id, limit=300, order="asc")
    if history and history.get("measurements"):
        render_glucose_chart(history)
    else:
        st.info("Not enough data yet to display trends.")

    # ── Recent alerts ────────────────────────────────
    active = api_client.get_active_alerts(patient_id)
    if active:
        st.markdown(
            f'<div class="section-header">Active Alerts ({len(active)})</div>',
            unsafe_allow_html=True,
        )
        render_alert_cards(active, key_prefix="pat_dash")
    else:
        st.markdown('<div class="section-header">Alerts</div>', unsafe_allow_html=True)
        st.markdown(
            "<div class='kpi-card text-center' style='padding:1.5rem;'>"
            "<div style='font-size:1.5rem;'>&#10003;</div>"
            "<div style='color:#10B981; font-weight:600;'>All clear</div>"
            "<div class='text-muted'>No active alerts at this time</div>"
            "</div>",
            unsafe_allow_html=True,
        )


def _render_device_status(patient_id: str) -> None:
    """Show connected devices."""
    devices = api_client.get_devices_for_patient(patient_id)
    if devices:
        st.markdown('<div class="section-header">Your Devices</div>', unsafe_allow_html=True)
        for d in devices:
            status = d.get("status", "unknown")
            color = "#10B981" if status == "active" else "#9CA3AF"
            st.markdown(
                f"<div class='kpi-card' style='text-align:left; margin-bottom:0.5rem;'>"
                f"<span style='color:{color}; font-size:1.2rem;'>&#9679;</span> "
                f"<strong>{d['device_id']}</strong> &mdash; {status.title()}"
                f"</div>",
                unsafe_allow_html=True,
            )
