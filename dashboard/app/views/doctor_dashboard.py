"""Doctor dashboard — multi-patient overview with severity prioritization."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.auth import navigate
from app.components.metrics_cards import render_kpi_row
from app.components.patient_cards import build_patient_summaries, render_patient_card
from app.components.alerts_list import render_alert_cards


def render() -> None:
    st.markdown(
        "<h2 style='margin-bottom:0.25rem;'>Clinical Dashboard</h2>"
        "<div class='text-muted mb-2'>Patient monitoring overview</div>",
        unsafe_allow_html=True,
    )

    patients = api_client.list_patients()
    if patients is None:
        st.error("Unable to connect to the backend service.")
        return
    if not patients:
        st.info("No patients registered yet. Waiting for sensor data...")
        return

    # ── Build summaries ──────────────────────────────
    summaries = build_patient_summaries(patients, api_client)

    # ── KPI row ──────────────────────────────────────
    total = len(summaries)
    n_critical = sum(1 for s in summaries if s["classification"] == "critical")
    n_warning = sum(1 for s in summaries if s["classification"] == "warning")
    n_alerts = sum(s["n_alerts"] for s in summaries)

    render_kpi_row([
        ("Patients Monitored", str(total), "#0066FF"),
        ("Critical", str(n_critical), "#EF4444" if n_critical else "#9CA3AF"),
        ("Warning", str(n_warning), "#F59E0B" if n_warning else "#9CA3AF"),
        ("Active Alerts", str(n_alerts), "#EF4444" if n_alerts else "#10B981"),
    ])

    # ── Patient cards (sorted by severity) ───────────
    st.markdown(
        '<div class="section-header">Patients</div>'
        '<div class="text-muted mb-1">Sorted by severity &mdash; most urgent first</div>',
        unsafe_allow_html=True,
    )

    for s in summaries:
        clicked = render_patient_card(s)
        if clicked:
            st.session_state.selected_patient_id = s["patient_id"]
            navigate("doctor_patient_detail")

    # ── Recent alerts ────────────────────────────────
    st.markdown(
        '<div class="section-header">Recent Alerts</div>',
        unsafe_allow_html=True,
    )
    all_alerts = api_client.list_alerts(limit=10)
    if all_alerts:
        render_alert_cards(all_alerts, show_patient=True, key_prefix="doc_dash")
    else:
        st.markdown(
            "<div class='kpi-card text-center' style='padding:1.5rem;'>"
            "<div style='color:#10B981; font-weight:600;'>No alerts</div>"
            "<div class='text-muted'>All patients are within normal range</div>"
            "</div>",
            unsafe_allow_html=True,
        )
