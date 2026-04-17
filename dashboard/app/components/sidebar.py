"""Role-based sidebar navigation."""

from __future__ import annotations

import streamlit as st

from app.auth import get_name, get_role, logout

_PATIENT_NAV = {
    "My Dashboard": "patient_dashboard",
    "My Alerts": "patient_alerts",
}

_DOCTOR_NAV = {
    "Dashboard": "doctor_dashboard",
    "Alerts Center": "doctor_alerts",
}

# Sub-pages map to their parent nav item for radio highlighting
_PARENT_MAP = {
    "doctor_patient_detail": "doctor_dashboard",
}


def _on_patient_nav() -> None:
    label = st.session_state.get("patient_nav_radio")
    page = _PATIENT_NAV.get(label)
    if page:
        st.session_state.current_page = page


def _on_doctor_nav() -> None:
    label = st.session_state.get("doctor_nav_radio")
    page = _DOCTOR_NAV.get(label)
    if page:
        st.session_state.current_page = page


def render_sidebar() -> None:
    """Render the role-based sidebar."""
    role = get_role()
    current = st.session_state.get("current_page", "")

    with st.sidebar:
        st.markdown(
            "<div style='font-size:1.4rem; font-weight:700; color:#0066FF; "
            "margin-bottom:0.5rem;'>GlucoWatch</div>",
            unsafe_allow_html=True,
        )
        st.caption("Glucose Monitoring Platform")
        st.divider()

        if role == "patient":
            nav_map = _PATIENT_NAV
            nav_keys = list(nav_map.keys())
            nav_values = list(nav_map.values())
            try:
                idx = nav_values.index(current)
            except ValueError:
                idx = 0

            st.radio(
                "Navigation",
                nav_keys,
                index=idx,
                key="patient_nav_radio",
                on_change=_on_patient_nav,
                label_visibility="collapsed",
            )

        elif role == "doctor":
            nav_map = _DOCTOR_NAV
            nav_keys = list(nav_map.keys())
            nav_values = list(nav_map.values())
            effective = _PARENT_MAP.get(current, current)
            try:
                idx = nav_values.index(effective)
            except ValueError:
                idx = 0

            st.radio(
                "Navigation",
                nav_keys,
                index=idx,
                key="doctor_nav_radio",
                on_change=_on_doctor_nav,
                label_visibility="collapsed",
            )

        st.divider()

        # User info
        st.markdown(
            f"<div style='font-size:0.9rem;'>"
            f"<strong>{get_name()}</strong><br>"
            f"<span style='color:#6B7280; font-size:0.8rem;'>"
            f"{'Patient' if role == 'patient' else 'Healthcare Provider'}"
            f"</span></div>",
            unsafe_allow_html=True,
        )

        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Sign Out", use_container_width=True):
            logout()
            st.rerun()
