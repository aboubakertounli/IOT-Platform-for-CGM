"""Doctor Dashboard — multi-patient overview with prioritization."""

from __future__ import annotations

import streamlit as st

from app import api_client
from app.components.metrics_cards import render_patient_summary_card
from app.components.alerts_table import render_alerts_table
from app.components.charts import render_glucose_history_chart


_SEVERITY_PRIORITY = {"critical": 0, "warning": 1, "info": 2}


def render() -> None:
    """Render the full doctor dashboard page."""
    st.header("Doctor Dashboard")

    patients = api_client.list_patients()
    if patients is None:
        st.error("Cannot reach backend. Is the server running?")
        return
    if not patients:
        st.warning("No patients registered yet.")
        return

    # ── Global alerts panel ───────────────────────────
    with st.expander("Global Alerts Panel", expanded=True):
        all_alerts = api_client.list_alerts(limit=50)
        if all_alerts:
            render_alerts_table(all_alerts, show_patient=True)
        else:
            st.success("No alerts across all patients.")

    st.markdown("---")

    # ── Build patient summaries with severity ranking ─
    summaries = []
    for p in patients:
        pid = p["patient_id"]
        latest = api_client.get_latest_glucose(pid)
        active = api_client.get_active_alerts(pid)
        worst = _worst_severity(active)
        summaries.append({
            "patient_id": pid,
            "patient": p,
            "latest": latest,
            "active_alerts": active,
            "worst_severity": worst,
            "priority": _SEVERITY_PRIORITY.get(worst, 3),
            "n_active": len(active) if active else 0,
        })

    # Sort: most severe first, then by number of active alerts descending
    summaries.sort(key=lambda s: (s["priority"], -s["n_active"]))

    # ── Patient overview cards ────────────────────────
    st.subheader("Patient Overview")
    st.caption("Sorted by severity — most urgent first")

    for s in summaries:
        render_patient_summary_card(s["patient_id"], s["latest"], s["active_alerts"])

    st.markdown("---")

    # ── Drill-down ────────────────────────────────────
    st.subheader("Patient Drill-Down")
    drill_options = [s["patient_id"] for s in summaries]
    selected = st.selectbox(
        "Select a patient for details",
        options=drill_options,
        key="doctor_drilldown",
    )

    if selected:
        _render_drilldown(selected)


def _worst_severity(alerts: list[dict] | None) -> str:
    """Return the worst severity level among active alerts."""
    if not alerts:
        return "info"
    worst = "info"
    for a in alerts:
        sev = a.get("severity", "info")
        if _SEVERITY_PRIORITY.get(sev, 3) < _SEVERITY_PRIORITY.get(worst, 3):
            worst = sev
    return worst


def _render_drilldown(patient_id: str) -> None:
    """Show detailed view for a single patient within the doctor page."""
    col1, col2 = st.columns(2)

    with col1:
        stats = api_client.get_glucose_stats(patient_id)
        if stats:
            st.markdown("**Statistics**")
            st.metric("Measurements", stats.get("count", 0))
            avg = stats.get("avg_glucose")
            st.metric("Avg Glucose", f"{avg:.1f} mg/dL" if avg else "N/A")
            st.metric(
                "Range",
                f"{stats.get('min_glucose', 0):.0f} – {stats.get('max_glucose', 0):.0f} mg/dL"
                if stats.get("min_glucose") is not None else "N/A",
            )

    with col2:
        analysis = api_client.get_latest_analysis(patient_id)
        if analysis:
            st.markdown("**Latest Analysis**")
            st.metric("Classification", analysis.get("classification", "N/A").upper())
            st.metric("Trend", analysis.get("trend_direction", "N/A").replace("_", " ").title())
            st.metric("Anomaly", "Yes" if analysis.get("is_anomaly") else "No")

    # Chart
    history = api_client.get_glucose_history(patient_id, limit=200, order="asc")
    if history:
        render_glucose_history_chart(history)

    # Patient alerts
    alerts = api_client.get_alerts_for_patient(patient_id, limit=20)
    if alerts:
        st.markdown("**Recent Alerts**")
        render_alerts_table(alerts)
