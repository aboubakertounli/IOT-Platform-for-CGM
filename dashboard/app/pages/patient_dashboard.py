"""Patient Dashboard — single-patient detailed view."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.components.patient_selector import render_patient_selector
from app.components.metrics_cards import render_glucose_metric, render_stats_cards
from app.components.charts import render_glucose_history_chart
from app.components.alerts_table import render_alerts_table


def render() -> None:
    """Render the full patient dashboard page."""
    st.header("Patient Dashboard")

    patient_id = render_patient_selector(key="patient_page_select")
    if patient_id is None:
        return

    st.markdown("---")

    # ── Latest reading + analysis ─────────────────────
    latest = api_client.get_latest_glucose(patient_id)
    analysis = api_client.get_latest_analysis(patient_id)

    if latest is None and analysis is None:
        st.warning(f"No glucose data yet for **{patient_id}**. Waiting for sensor readings...")
        _render_devices_section(patient_id)
        return

    if latest:
        render_glucose_metric(latest)

    st.markdown("---")

    # ── Analysis detail ───────────────────────────────
    if analysis:
        st.subheader("Analysis")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Anomaly", "Yes" if analysis.get("is_anomaly") else "No")
        with col2:
            st.metric("Anomaly Score", f"{analysis.get('anomaly_score', 0):.2f}")
        with col3:
            st.metric(
                "Trend Rate",
                f"{analysis.get('trend_rate_mg_dl_per_min', 0):+.2f} mg/dL/min",
            )
        st.markdown("---")

    # ── Statistics ────────────────────────────────────
    stats = api_client.get_glucose_stats(patient_id)
    if stats:
        st.subheader("Statistics")
        render_stats_cards(stats)
        st.markdown("---")

    # ── History chart ─────────────────────────────────
    st.subheader("Glucose History")
    limit = st.slider("Number of readings", 50, 500, 200, step=50, key="hist_limit")
    history = api_client.get_glucose_history(patient_id, limit=limit, order="asc")
    if history:
        render_glucose_history_chart(history)
    else:
        st.info("No history data available.")

    st.markdown("---")

    # ── Alerts ────────────────────────────────────────
    st.subheader("Alerts")
    tab_active, tab_all = st.tabs(["Active Alerts", "All Alerts"])

    with tab_active:
        active_alerts = api_client.get_active_alerts(patient_id)
        if active_alerts:
            render_alerts_table(active_alerts)
        else:
            st.success("No active alerts.")

    with tab_all:
        all_alerts = api_client.get_alerts_for_patient(patient_id, limit=50)
        if all_alerts:
            render_alerts_table(all_alerts)
        else:
            st.info("No alert history.")

    st.markdown("---")

    # ── Devices ───────────────────────────────────────
    _render_devices_section(patient_id)


def _render_devices_section(patient_id: str) -> None:
    """Show devices associated with this patient."""
    st.subheader("Devices")
    devices = api_client.get_devices_for_patient(patient_id)
    if devices:
        for d in devices:
            status_icon = "🟢" if d.get("status") == "active" else "⚪"
            st.markdown(
                f"{status_icon} **{d['device_id']}** — "
                f"Status: {d.get('status', 'unknown')} — "
                f"Since: {d.get('created_at', 'N/A')[:10]}"
            )
    else:
        st.info("No devices registered for this patient.")
