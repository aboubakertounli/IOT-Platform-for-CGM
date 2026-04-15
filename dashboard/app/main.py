"""CGM IoT Platform — Streamlit Dashboard Entry Point."""

import time

import streamlit as st

from app import api_client
from app.components.sidebar import render_sidebar
from app.pages import patient_dashboard, doctor_dashboard

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="CGM IoT Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Session state defaults ────────────────────────────
if "auto_refresh" not in st.session_state:
    st.session_state["auto_refresh"] = True
if "refresh_interval" not in st.session_state:
    st.session_state["refresh_interval"] = 30


def main() -> None:
    # ── Backend connectivity check ────────────────────
    health = api_client.check_health()
    if health is None:
        st.error(
            "**Backend unreachable.** Make sure the FastAPI server is running "
            "and the BACKEND_URL environment variable is set correctly."
        )
        st.stop()

    # ── Sidebar navigation ────────────────────────────
    page = render_sidebar()

    # ── Page routing ──────────────────────────────────
    if page == "Patient":
        patient_dashboard.render()
    elif page == "Doctor":
        doctor_dashboard.render()

    # ── Auto-refresh ──────────────────────────────────
    if st.session_state.get("auto_refresh"):
        interval = st.session_state.get("refresh_interval", 30)
        time.sleep(interval)
        st.rerun()


if __name__ == "__main__":
    main()
