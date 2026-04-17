"""Registration page with role selection."""

import streamlit as st

from app.auth import register, navigate
from app.styles import hide_sidebar


def render() -> None:
    hide_sidebar()

    st.markdown(
        """
        <div class="auth-title">Create your account</div>
        <div class="auth-subtitle">Join GlucoWatch as a patient or healthcare provider</div>
        """,
        unsafe_allow_html=True,
    )

    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("register_form"):
            name = st.text_input("Full name", placeholder="Your full name")
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Choose a password")

            st.markdown("**I am a:**")
            role = st.radio(
                "Role",
                options=["Patient", "Healthcare Provider"],
                horizontal=True,
                label_visibility="collapsed",
            )

            patient_id = None
            if role == "Patient":
                patient_id = st.text_input(
                    "Patient ID (from your sensor kit)",
                    placeholder="e.g. PAT-001",
                )

            submitted = st.form_submit_button("Create Account", use_container_width=True, type="primary")

            if submitted:
                if not name or not email or not password:
                    st.error("Please fill in all fields.")
                elif role == "Patient" and not patient_id:
                    st.error("Please enter your Patient ID.")
                else:
                    mapped_role = "patient" if role == "Patient" else "doctor"
                    if register(name, email, password, mapped_role, patient_id):
                        st.rerun()
                    else:
                        st.error("This email is already registered.")

        st.markdown("<div class='text-center mt-1'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back to home", use_container_width=True):
                navigate("landing")
        with c2:
            if st.button("Already have an account?", use_container_width=True):
                navigate("login")
        st.markdown("</div>", unsafe_allow_html=True)
