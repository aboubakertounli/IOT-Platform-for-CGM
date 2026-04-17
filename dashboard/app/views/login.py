"""Login page."""

import streamlit as st

from app.auth import login, navigate
from app.styles import hide_sidebar


def render() -> None:
    hide_sidebar()

    st.markdown(
        """
        <div class="auth-title">Welcome back</div>
        <div class="auth-subtitle">Sign in to your GlucoWatch account</div>
        """,
        unsafe_allow_html=True,
    )

    # Centered form
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        with st.form("login_form"):
            email = st.text_input("Email", placeholder="you@example.com")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Please fill in all fields.")
                elif login(email, password):
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

        st.markdown("<div class='text-center mt-1'>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1:
            if st.button("← Back to home", use_container_width=True):
                navigate("landing")
        with c2:
            if st.button("Create account →", use_container_width=True):
                navigate("register")
        st.markdown("</div>", unsafe_allow_html=True)

        # Demo hint
        st.markdown("<br>", unsafe_allow_html=True)
        st.info("**Demo:** Use `doctor@glucowatch.io` / `demo123` or `ahmed@glucowatch.io` / `demo123`")
