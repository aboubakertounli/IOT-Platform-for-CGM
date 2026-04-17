"""Session-state authentication (demo-grade, no real backend auth)."""

from __future__ import annotations

import streamlit as st

# Pre-configured demo accounts
_DEMO_USERS: dict[str, dict] = {
    "ahmed@glucowatch.io": {
        "password": "demo123",
        "role": "patient",
        "name": "Ahmed Tounli",
        "patient_id": "PAT-001",
    },
    "youssef@glucowatch.io": {
        "password": "demo123",
        "role": "patient",
        "name": "Youssef Amrani",
        "patient_id": "PAT-002",
    },
    "fatima@glucowatch.io": {
        "password": "demo123",
        "role": "patient",
        "name": "Fatima Zahra",
        "patient_id": "PAT-003",
    },
    "doctor@glucowatch.io": {
        "password": "demo123",
        "role": "doctor",
        "name": "Dr. Sarah Chen",
    },
}

_DEFAULTS = {
    "authenticated": False,
    "user_role": None,
    "user_name": None,
    "user_email": None,
    "patient_id": None,
    "current_page": "landing",
    "selected_patient_id": None,
}


def init_auth() -> None:
    """Initialize session state with auth defaults."""
    for key, val in _DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = val


def login(email: str, password: str) -> bool:
    """Authenticate with demo credentials. Returns True on success."""
    user = _DEMO_USERS.get(email.lower().strip())
    if user and user["password"] == password:
        st.session_state.authenticated = True
        st.session_state.user_role = user["role"]
        st.session_state.user_name = user["name"]
        st.session_state.user_email = email.lower().strip()
        st.session_state.patient_id = user.get("patient_id")
        st.session_state.current_page = (
            "patient_dashboard" if user["role"] == "patient" else "doctor_dashboard"
        )
        return True
    return False


def logout() -> None:
    """Clear auth state and return to landing."""
    for key, val in _DEFAULTS.items():
        st.session_state[key] = val


def register(
    name: str,
    email: str,
    password: str,
    role: str,
    patient_id: str | None = None,
) -> bool:
    """Register a new demo user and log them in."""
    email = email.lower().strip()
    if email in _DEMO_USERS:
        return False
    _DEMO_USERS[email] = {
        "password": password,
        "role": role,
        "name": name,
        "patient_id": patient_id,
    }
    return login(email, password)


def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)


def get_role() -> str | None:
    return st.session_state.get("user_role")


def get_name() -> str:
    return st.session_state.get("user_name", "")


def get_patient_id() -> str | None:
    return st.session_state.get("patient_id")


def navigate(page: str) -> None:
    """Navigate to a page and rerun."""
    st.session_state.current_page = page
    st.rerun()
