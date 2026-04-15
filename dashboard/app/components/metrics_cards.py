"""Metric card components for glucose data display."""

from __future__ import annotations

import streamlit as st


# ── Color mapping ─────────────────────────────────────

_CLASSIFICATION_COLORS = {
    "normal": "#2ecc71",
    "warning": "#f39c12",
    "critical": "#e74c3c",
    "unknown": "#95a5a6",
}

_TREND_ARROWS = {
    "rapid_rise": "arrow_upper_right",
    "rising": "arrow_upper_right",
    "stable": "arrow_right",
    "falling": "arrow_lower_right",
    "rapid_fall": "arrow_lower_right",
}

_SEVERITY_COLORS = {
    "critical": "#e74c3c",
    "warning": "#f39c12",
    "info": "#3498db",
}


def render_glucose_metric(latest: dict) -> None:
    """Display the current glucose reading as a prominent metric."""
    glucose = latest.get("glucose_mg_dl", 0)
    classification = latest.get("classification", "unknown")
    trend = latest.get("trend_direction", "stable")
    trend_rate = latest.get("trend_rate") or 0.0
    color = _CLASSIFICATION_COLORS.get(classification, "#95a5a6")
    arrow = _TREND_ARROWS.get(trend, "arrow_right")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Glucose",
            value=f"{glucose:.0f} mg/dL",
            delta=f"{trend_rate:+.1f} mg/dL/min" if trend_rate else None,
        )

    with col2:
        st.markdown(
            f"**Classification**<br>"
            f"<span style='color:{color}; font-size:1.4rem; font-weight:bold'>"
            f"{classification.upper()}</span>",
            unsafe_allow_html=True,
        )

    with col3:
        trend_label = trend.replace("_", " ").title() if trend else "Stable"
        st.markdown(
            f"**Trend**<br>"
            f":{arrow}: **{trend_label}**",
            unsafe_allow_html=True,
        )


def render_stats_cards(stats: dict) -> None:
    """Display glucose statistics in a row of metrics."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Measurements", stats.get("count", 0))
    with col2:
        min_g = stats.get("min_glucose")
        st.metric("Min", f"{min_g:.0f}" if min_g is not None else "N/A")
    with col3:
        max_g = stats.get("max_glucose")
        st.metric("Max", f"{max_g:.0f}" if max_g is not None else "N/A")
    with col4:
        avg_g = stats.get("avg_glucose")
        st.metric("Average", f"{avg_g:.1f}" if avg_g is not None else "N/A")


def render_patient_summary_card(
    patient_id: str,
    latest: dict | None,
    active_alerts: list[dict] | None,
) -> None:
    """Compact card for doctor overview — one patient."""
    glucose = latest.get("glucose_mg_dl", 0) if latest else None
    classification = latest.get("classification", "unknown") if latest else "unknown"
    trend = latest.get("trend_direction", "stable") if latest else "stable"
    color = _CLASSIFICATION_COLORS.get(classification, "#95a5a6")
    n_alerts = len(active_alerts) if active_alerts else 0

    # Determine severity priority for sorting
    severity_order = {"critical": 0, "warning": 1, "info": 2}
    worst = "info"
    if active_alerts:
        for a in active_alerts:
            sev = a.get("severity", "info")
            if severity_order.get(sev, 3) < severity_order.get(worst, 3):
                worst = sev
    border_color = _SEVERITY_COLORS.get(worst, "#3498db") if n_alerts > 0 else "#ecf0f1"

    st.markdown(
        f"""
        <div style="border-left: 4px solid {border_color}; padding: 0.8rem 1rem;
                    background: #1e1e1e; border-radius: 6px; margin-bottom: 0.5rem;">
            <strong style="font-size:1.1rem">{patient_id}</strong><br>
            <span style="color:{color}; font-weight:bold">
                {f"{glucose:.0f} mg/dL" if glucose else "No data"}
            </span>
            &nbsp;|&nbsp; {classification.upper()}
            &nbsp;|&nbsp; {trend.replace("_"," ").title()}
            &nbsp;|&nbsp; Alerts: <strong>{n_alerts}</strong>
        </div>
        """,
        unsafe_allow_html=True,
    )
