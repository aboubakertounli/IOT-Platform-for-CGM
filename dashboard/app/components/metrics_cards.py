"""Styled KPI and metric components."""

from __future__ import annotations

import streamlit as st

# ── Color tokens ──────────────────────────────────────
_STATUS_COLORS = {
    "normal": "#10B981",
    "warning": "#F59E0B",
    "critical": "#EF4444",
    "unknown": "#9CA3AF",
}

_STATUS_LABELS = {
    "normal": "Normal",
    "warning": "Attention Required",
    "critical": "Critical",
    "unknown": "Unknown",
}

_TREND_LABELS = {
    "rapid_rise": "Rising Rapidly",
    "rising": "Rising",
    "stable": "Stable",
    "falling": "Falling",
    "rapid_fall": "Falling Rapidly",
}

_TREND_ICONS = {
    "rapid_rise": "&#8599;&#8599;",
    "rising": "&#8599;",
    "stable": "&#8594;",
    "falling": "&#8600;",
    "rapid_fall": "&#8600;&#8600;",
}

# Human-readable status messages for patients
_PATIENT_MESSAGES = {
    "normal": "Your glucose level is within the normal range. Keep it up!",
    "warning": "Your glucose requires attention. Please monitor closely.",
    "critical": "Your glucose is at a critical level. Consider contacting your healthcare provider.",
    "unknown": "Waiting for enough data to determine your glucose status.",
}

_MSG_STYLES = {
    "normal": "background:#D1FAE5; color:#065F46;",
    "warning": "background:#FEF3C7; color:#92400E;",
    "critical": "background:#FEE2E2; color:#991B1B;",
    "unknown": "background:#F3F4F6; color:#374151;",
}


def render_glucose_hero(latest: dict) -> None:
    """Big, prominent glucose display for the patient dashboard."""
    glucose = latest.get("glucose_mg_dl", 0)
    classification = latest.get("classification", "unknown")
    trend = latest.get("trend_direction", "stable")
    color = _STATUS_COLORS.get(classification, "#9CA3AF")
    trend_label = _TREND_LABELS.get(trend, "Stable")
    trend_icon = _TREND_ICONS.get(trend, "&#8594;")
    badge_class = f"badge-{classification}" if classification in _STATUS_COLORS else "badge-info"
    message = _PATIENT_MESSAGES.get(classification, "")
    msg_style = _MSG_STYLES.get(classification, "")

    st.markdown(
        f"""
        <div class="glucose-hero">
            <div class="glucose-value" style="color:{color};">{glucose:.0f}</div>
            <div class="glucose-unit">mg/dL</div>
            <div style="margin-top:0.75rem;">
                <span class="badge {badge_class}">{_STATUS_LABELS.get(classification, 'Unknown')}</span>
                &nbsp;&nbsp;
                <span class="badge badge-stable">{trend_icon} {trend_label}</span>
            </div>
            <div class="glucose-status-msg" style="{msg_style}">
                {message}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_row(items: list[tuple[str, str, str]]) -> None:
    """Render a row of KPI cards. Each item: (label, value, color)."""
    cols = st.columns(len(items))
    for col, (label, value, color) in zip(cols, items):
        with col:
            st.markdown(
                f"""
                <div class="kpi-card">
                    <div class="kpi-value" style="color:{color};">{value}</div>
                    <div class="kpi-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


def render_stats_row(stats: dict) -> None:
    """Glucose statistics as a KPI row."""
    count = stats.get("count", 0)
    min_g = stats.get("min_glucose")
    max_g = stats.get("max_glucose")
    avg_g = stats.get("avg_glucose")

    items = [
        ("Readings", str(count), "#0066FF"),
        ("Min", f"{min_g:.0f}" if min_g is not None else "—", "#10B981"),
        ("Max", f"{max_g:.0f}" if max_g is not None else "—", "#EF4444"),
        ("Average", f"{avg_g:.1f}" if avg_g is not None else "—", "#6B7280"),
    ]
    render_kpi_row(items)
