"""Plotly chart components for glucose visualization."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st


_ZONE_COLORS = {
    "critical_low": "rgba(231,76,60,0.12)",
    "warning_low": "rgba(243,156,18,0.12)",
    "normal": "rgba(46,204,113,0.08)",
    "warning_high": "rgba(243,156,18,0.12)",
    "critical_high": "rgba(231,76,60,0.12)",
}

# Default glucose thresholds (mg/dL)
_HYPO_CRITICAL = 54
_HYPO_WARNING = 70
_HYPER_WARNING = 180
_HYPER_CRITICAL = 250


def render_glucose_history_chart(history: dict) -> None:
    """Render a time-series line chart of glucose measurements."""
    measurements = history.get("measurements", [])
    if not measurements:
        st.info("No history data available.")
        return

    df = pd.DataFrame(measurements)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    fig = go.Figure()

    # Threshold zones
    y_min = max(0, df["glucose_mg_dl"].min() - 20)
    y_max = df["glucose_mg_dl"].max() + 20

    _add_zone(fig, y_min, _HYPO_CRITICAL, _ZONE_COLORS["critical_low"], "Severe Hypo")
    _add_zone(fig, _HYPO_CRITICAL, _HYPO_WARNING, _ZONE_COLORS["warning_low"], "Hypo")
    _add_zone(fig, _HYPO_WARNING, _HYPER_WARNING, _ZONE_COLORS["normal"], "Normal")
    _add_zone(fig, _HYPER_WARNING, _HYPER_CRITICAL, _ZONE_COLORS["warning_high"], "Hyper")
    _add_zone(fig, _HYPER_CRITICAL, y_max, _ZONE_COLORS["critical_high"], "Severe Hyper")

    # Glucose line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["glucose_mg_dl"],
        mode="lines+markers",
        name="Glucose",
        line=dict(color="#3498db", width=2),
        marker=dict(size=4),
        hovertemplate="<b>%{x|%H:%M:%S}</b><br>%{y:.0f} mg/dL<extra></extra>",
    ))

    # Anomaly markers
    anomalies = df[df.get("is_anomaly", pd.Series(dtype=bool)) == True]  # noqa: E712
    if not anomalies.empty:
        fig.add_trace(go.Scatter(
            x=anomalies["timestamp"],
            y=anomalies["glucose_mg_dl"],
            mode="markers",
            name="Anomaly",
            marker=dict(color="#e74c3c", size=10, symbol="x"),
            hovertemplate="<b>ANOMALY</b><br>%{x|%H:%M:%S}<br>%{y:.0f} mg/dL<extra></extra>",
        ))

    fig.update_layout(
        title="Glucose History",
        xaxis_title="Time",
        yaxis_title="Glucose (mg/dL)",
        height=400,
        margin=dict(l=40, r=20, t=40, b=40),
        legend=dict(orientation="h", y=-0.15),
        hovermode="x unified",
    )
    fig.update_yaxes(range=[y_min, y_max])

    st.plotly_chart(fig, use_container_width=True)


def _add_zone(
    fig: go.Figure,
    y0: float,
    y1: float,
    color: str,
    name: str,
) -> None:
    """Add a colored horizontal zone to the chart."""
    fig.add_hrect(
        y0=y0, y1=y1,
        fillcolor=color,
        line_width=0,
        annotation_text=name,
        annotation_position="top left",
        annotation_font_size=9,
        annotation_font_color="gray",
    )
