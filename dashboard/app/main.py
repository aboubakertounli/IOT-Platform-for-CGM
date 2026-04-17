"""GlucoWatch — Streamlit Dashboard Entry Point."""

import time

import streamlit as st

from app.auth import init_auth, is_authenticated, get_role
from app.styles import inject_global_styles
from app.components.sidebar import render_sidebar

from app.views import (
    landing,
    login,
    register,
    patient_dashboard,
    patient_alerts,
    doctor_dashboard,
    doctor_patient_detail,
    doctor_alerts,
)

# ── Page config ───────────────────────────────────────
st.set_page_config(
    page_title="GlucoWatch",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Init ──────────────────────────────────────────────
init_auth()
inject_global_styles()

# ── Auto-refresh defaults ─────────────────────────────
if "auto_refresh" not in st.session_state:
    st.session_state["auto_refresh"] = False
if "refresh_interval" not in st.session_state:
    st.session_state["refresh_interval"] = 30

# ── Page registry ─────────────────────────────────────
_PUBLIC_PAGES = {
    "landing": landing.render,
    "login": login.render,
    "register": register.render,
}

_PATIENT_PAGES = {
    "patient_dashboard": patient_dashboard.render,
    "patient_alerts": patient_alerts.render,
}

_DOCTOR_PAGES = {
    "doctor_dashboard": doctor_dashboard.render,
    "doctor_patient_detail": doctor_patient_detail.render,
    "doctor_alerts": doctor_alerts.render,
}


def main() -> None:
    current = st.session_state.get("current_page", "landing")

    # ── Public pages (no sidebar) ─────────────────────
    if not is_authenticated():
        renderer = _PUBLIC_PAGES.get(current, landing.render)
        renderer()
        return

    # ── Authenticated pages ───────────────────────────
    render_sidebar()
    role = get_role()

    if role == "patient":
        renderer = _PATIENT_PAGES.get(current, patient_dashboard.render)
    elif role == "doctor":
        renderer = _DOCTOR_PAGES.get(current, doctor_dashboard.render)
    else:
        st.error("Unknown user role.")
        return

    renderer()

    # ── Auto-refresh ──────────────────────────────────
    if st.session_state.get("auto_refresh"):
        interval = st.session_state.get("refresh_interval", 30)
        time.sleep(interval)
        st.rerun()


main()
