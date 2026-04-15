"""Patient selector component."""

from __future__ import annotations

import streamlit as st

from app import api_client


def render_patient_selector(key: str = "patient_select") -> str | None:
    """Fetch patients and render a selectbox. Returns selected patient_id or None."""
    patients = api_client.list_patients()

    if patients is None:
        st.error("Cannot reach backend. Is the server running?")
        return None

    if not patients:
        st.warning("No patients registered yet. Start the edge simulator to send data.")
        return None

    options = [p["patient_id"] for p in patients]
    labels = {
        p["patient_id"]: (
            f"{p['patient_id']}"
            + (f" — {p['first_name']} {p['last_name']}" if p.get("first_name") else "")
        )
        for p in patients
    }

    selected = st.selectbox(
        "Select patient",
        options=options,
        format_func=lambda x: labels.get(x, x),
        key=key,
    )
    return selected
