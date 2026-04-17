"""Plotly chart components — light theme."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

_HYPO_CRITICAL = 54
_HYPO_WARNING = 70
_HYPER_WARNING = 180
_HYPER_CRITICAL = 250


def render_glucose_chart(history: dict, height: int = 380) -> None:
    """Time-series glucose chart with threshold zones."""
    measurements = history.get("measurements", [])
    if not measurements:
        st.info("No history data available yet.")
        return

    df = pd.DataFrame(measurements)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")

    fig = go.Figure()

    y_min = max(0, df["glucose_mg_dl"].min() - 20)
    y_max = df["glucose_mg_dl"].max() + 20

    # Threshold zones
    _zone(fig, y_min, _HYPO_CRITICAL, "rgba(239,68,68,0.08)", "Severe Hypo")
    _zone(fig, _HYPO_CRITICAL, _HYPO_WARNING, "rgba(245,158,11,0.08)", "Hypo")
    _zone(fig, _HYPO_WARNING, _HYPER_WARNING, "rgba(16,185,129,0.06)", "Normal Range")
    _zone(fig, _HYPER_WARNING, _HYPER_CRITICAL, "rgba(245,158,11,0.08)", "Hyper")
    _zone(fig, _HYPER_CRITICAL, y_max, "rgba(239,68,68,0.08)", "Severe Hyper")

    # Threshold lines
    for val, color, dash in [
        (_HYPO_CRITICAL, "#EF4444", "dot"),
        (_HYPO_WARNING, "#F59E0B", "dash"),
        (_HYPER_WARNING, "#F59E0B", "dash"),
        (_HYPER_CRITICAL, "#EF4444", "dot"),
    ]:
        fig.add_hline(y=val, line_color=color, line_dash=dash, line_width=1, opacity=0.5)

    # Glucose line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["glucose_mg_dl"],
        mode="lines",
        name="Glucose",
        line=dict(color="#0066FF", width=2.5),
        fill="tozeroy",
        fillcolor="rgba(0,102,255,0.04)",
        hovertemplate="<b>%{x|%H:%M}</b><br>%{y:.0f} mg/dL<extra></extra>",
    ))

    # Anomaly markers
    if "is_anomaly" in df.columns:
        anomalies = df[df["is_anomaly"] == True]  # noqa: E712
        if not anomalies.empty:
            fig.add_trace(go.Scatter(
                x=anomalies["timestamp"],
                y=anomalies["glucose_mg_dl"],
                mode="markers",
                name="Anomaly",
                marker=dict(color="#EF4444", size=9, symbol="diamond-open", line_width=2),
                hovertemplate="<b>Anomaly</b><br>%{x|%H:%M}<br>%{y:.0f} mg/dL<extra></extra>",
            ))

    fig.update_layout(
        height=height,
        margin=dict(l=0, r=0, t=10, b=0),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            title=None,
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#F3F4F6",
            title="mg/dL",
            range=[y_min, y_max],
        ),
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center"),
        hovermode="x unified",
    )

    st.plotly_chart(fig, use_container_width=True)


def _zone(fig: go.Figure, y0: float, y1: float, color: str, name: str) -> None:
    fig.add_hrect(
        y0=y0, y1=y1,
        fillcolor=color,
        line_width=0,
        annotation_text=name,
        annotation_position="top left",
        annotation_font_size=8,
        annotation_font_color="#9CA3AF",
    )
