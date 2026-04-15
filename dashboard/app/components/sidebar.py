"""Sidebar navigation component."""

import streamlit as st

from app.config import REFRESH_INTERVAL_SECONDS


def render_sidebar() -> str:
    """Render sidebar and return the selected page name."""
    with st.sidebar:
        st.title("CGM IoT Platform")
        st.markdown("---")

        page = st.radio(
            "Navigation",
            options=["Patient", "Doctor"],
            index=0,
            label_visibility="collapsed",
        )

        st.markdown("---")

        # Auto-refresh toggle
        auto_refresh = st.toggle("Auto-refresh", value=True)
        if auto_refresh:
            interval = st.slider(
                "Interval (s)",
                min_value=10,
                max_value=120,
                value=REFRESH_INTERVAL_SECONDS,
                step=5,
            )
            st.session_state["auto_refresh"] = True
            st.session_state["refresh_interval"] = interval
        else:
            st.session_state["auto_refresh"] = False

        if st.button("Refresh now", use_container_width=True):
            st.rerun()

        st.markdown("---")
        st.caption("CGM IoT Platform v1.0")

    return page
