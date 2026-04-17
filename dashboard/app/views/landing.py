"""Landing page — public entry point."""

import streamlit as st

from app.auth import navigate
from app.styles import hide_sidebar


def render() -> None:
    hide_sidebar()

    # Hero
    st.markdown(
        """
        <div class="hero-section">
            <div class="hero-brand">GlucoWatch</div>
            <div class="hero-tagline">
                Continuous Glucose Monitoring, Simplified
            </div>
            <div class="hero-sub">
                Real-time monitoring, intelligent alerts, and clinical insights
                for patients and healthcare providers.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # CTA buttons
    _, col_l, col_r, _ = st.columns([1.5, 1, 1, 1.5])
    with col_l:
        if st.button("Sign In", use_container_width=True, type="primary"):
            navigate("login")
    with col_r:
        if st.button("Create Account", use_container_width=True):
            navigate("register")

    st.markdown("<br>", unsafe_allow_html=True)

    # Feature cards
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">📡</div>
                <div class="feature-title">Real-Time Monitoring</div>
                <div class="feature-desc">
                    Continuous glucose data streamed from CGM sensors,
                    analyzed and displayed in real time.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🔔</div>
                <div class="feature-title">Smart Alerts</div>
                <div class="feature-desc">
                    Automatic detection of hypo&shy;glycemia, hyper&shy;glycemia,
                    rapid trends, and anomalies.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="feature-card">
                <div class="feature-icon">🩺</div>
                <div class="feature-title">Clinical Dashboard</div>
                <div class="feature-desc">
                    Multi-patient overview for healthcare providers
                    with severity-based prioritization.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # How it works
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(
        """
        <div class="text-center">
            <div class="section-header" style="border:none; display:inline-block;">
                How It Works
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    h1, h2, h3 = st.columns(3)
    with h1:
        st.markdown(
            """<div class="text-center">
            <div style="font-size:1.5rem; font-weight:700; color:#0066FF;">1</div>
            <strong>Sensor Streams</strong><br>
            <span class="text-muted">CGM device sends glucose readings via IoT protocol</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with h2:
        st.markdown(
            """<div class="text-center">
            <div style="font-size:1.5rem; font-weight:700; color:#0066FF;">2</div>
            <strong>Analysis Engine</strong><br>
            <span class="text-muted">Classification, trend detection, and anomaly scoring</span>
            </div>""",
            unsafe_allow_html=True,
        )
    with h3:
        st.markdown(
            """<div class="text-center">
            <div style="font-size:1.5rem; font-weight:700; color:#0066FF;">3</div>
            <strong>Actionable Insights</strong><br>
            <span class="text-muted">Clear dashboards and smart alerts for patients and doctors</span>
            </div>""",
            unsafe_allow_html=True,
        )

    # Demo credentials hint
    st.markdown("<br><br>", unsafe_allow_html=True)
    with st.expander("Demo Credentials"):
        st.markdown(
            """
            | Role | Email | Password |
            |------|-------|----------|
            | Patient (Ahmed) | `ahmed@glucowatch.io` | `demo123` |
            | Patient (Youssef) | `youssef@glucowatch.io` | `demo123` |
            | Patient (Fatima) | `fatima@glucowatch.io` | `demo123` |
            | Doctor | `doctor@glucowatch.io` | `demo123` |
            """
        )
