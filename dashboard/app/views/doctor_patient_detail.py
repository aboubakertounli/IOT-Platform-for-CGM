"""Doctor — patient detail page (drill-down from dashboard)."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.auth import navigate
from app.config import get_patient_profile
from app.components.metrics_cards import render_glucose_hero, render_stats_row
from app.components.charts import render_glucose_chart
from app.components.alerts_list import render_alert_cards


def render() -> None:
    patient_id = st.session_state.get("selected_patient_id")
    if not patient_id:
        navigate("doctor_dashboard")
        return

    profile = get_patient_profile(patient_id)

    # Back button + header
    if st.button("← Back to Dashboard"):
        navigate("doctor_dashboard")

    st.markdown(
        f"<h2 style='margin-bottom:0.1rem;'>{profile['name']}</h2>"
        f"<div class='text-muted mb-2'>"
        f"{patient_id} &middot; Age {profile['age']} &middot; {profile['type']}"
        f"</div>",
        unsafe_allow_html=True,
    )

    # ── Current glucose ──────────────────────────────
    latest = api_client.get_latest_glucose(patient_id)
    if latest:
        render_glucose_hero(latest)
    else:
        st.info("No glucose data available for this patient.")
        return

    # ── Stats ─────────────────────────────────────────
    stats = api_client.get_glucose_stats(patient_id)
    if stats and stats.get("count", 0) > 0:
        st.markdown('<div class="section-header">Statistics</div>', unsafe_allow_html=True)
        render_stats_row(stats)

    # ── Chart ─────────────────────────────────────────
    st.markdown('<div class="section-header">Glucose Trend</div>', unsafe_allow_html=True)
    history = api_client.get_glucose_history(patient_id, limit=300, order="asc")
    if history and history.get("measurements"):
        render_glucose_chart(history)

    # ── Analysis ──────────────────────────────────────
    analysis = api_client.get_latest_analysis(patient_id)
    if analysis:
        st.markdown('<div class="section-header">Latest Analysis</div>', unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Classification", analysis.get("classification", "—").upper())
        with c2:
            trend = analysis.get("trend_direction", "—").replace("_", " ").title()
            st.metric("Trend", trend)
        with c3:
            rate = analysis.get("trend_rate_mg_dl_per_min", 0)
            st.metric("Rate", f"{rate:+.2f} mg/dL/min")

    # ── Alerts ────────────────────────────────────────
    active = api_client.get_active_alerts(patient_id)
    if active:
        st.markdown(
            f'<div class="section-header">Active Alerts ({len(active)})</div>',
            unsafe_allow_html=True,
        )
        render_alert_cards(active, allow_ack=True, key_prefix="doc_detail_active")

    all_alerts = api_client.get_alerts_for_patient(patient_id, limit=20)
    if all_alerts:
        st.markdown('<div class="section-header">Alert History</div>', unsafe_allow_html=True)
        render_alert_cards(all_alerts, key_prefix="doc_detail_hist")

    # ── Devices ───────────────────────────────────────
    devices = api_client.get_devices_for_patient(patient_id)
    if devices:
        st.markdown('<div class="section-header">Devices</div>', unsafe_allow_html=True)
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
