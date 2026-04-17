"""Design system — CSS injection for the dashboard."""

import streamlit as st


def inject_global_styles() -> None:
    """Inject the global CSS design system."""
    st.markdown(_GLOBAL_CSS, unsafe_allow_html=True)


def hide_sidebar() -> None:
    """Hide sidebar on public pages (landing, login, register)."""
    st.markdown(
        """<style>
        section[data-testid="stSidebar"] { display: none !important; }
        [data-testid="stSidebarCollapsedControl"] { display: none !important; }
        </style>""",
        unsafe_allow_html=True,
    )


_GLOBAL_CSS = """<style>
/* ── Reset & branding ──────────────────────────── */
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* ── KPI card ──────────────────────────────────── */
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    text-align: center;
}
.kpi-value {
    font-size: 2rem;
    font-weight: 700;
    line-height: 1.2;
    margin: 0.25rem 0;
}
.kpi-label {
    font-size: 0.85rem;
    color: #6B7280;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.03em;
}

/* ── Glucose hero ──────────────────────────────── */
.glucose-hero {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    margin-bottom: 1rem;
}
.glucose-value {
    font-size: 4rem;
    font-weight: 800;
    line-height: 1;
}
.glucose-unit {
    font-size: 1.1rem;
    color: #6B7280;
    margin-top: 0.25rem;
}
.glucose-status-msg {
    font-size: 1rem;
    margin-top: 1rem;
    padding: 0.6rem 1rem;
    border-radius: 8px;
    display: inline-block;
}

/* ── Status badges ─────────────────────────────── */
.badge {
    display: inline-block;
    padding: 4px 14px;
    border-radius: 20px;
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.badge-normal  { background: #D1FAE5; color: #065F46; }
.badge-warning { background: #FEF3C7; color: #92400E; }
.badge-critical { background: #FEE2E2; color: #991B1B; }
.badge-info    { background: #DBEAFE; color: #1E40AF; }
.badge-stable  { background: #E0E7FF; color: #3730A3; }

/* ── Patient card (doctor view) ────────────────── */
.patient-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 0.75rem;
    border-left: 5px solid #E5E7EB;
    box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    transition: box-shadow 0.2s ease;
}
.patient-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.1); }
.patient-card-normal  { border-left-color: #10B981; }
.patient-card-warning { border-left-color: #F59E0B; }
.patient-card-critical { border-left-color: #EF4444; }
.patient-card-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1A1D29;
}
.patient-card-id {
    font-size: 0.8rem;
    color: #6B7280;
}
.patient-card-glucose {
    font-size: 1.4rem;
    font-weight: 700;
    margin: 0.3rem 0;
}
.patient-card-meta {
    font-size: 0.85rem;
    color: #6B7280;
}

/* ── Alert card ────────────────────────────────── */
.alert-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 8px;
    padding: 0.8rem 1rem;
    margin-bottom: 0.5rem;
    border-left: 4px solid #E5E7EB;
}
.alert-card-critical { border-left-color: #EF4444; background: #FEF2F2; }
.alert-card-warning  { border-left-color: #F59E0B; background: #FFFBEB; }
.alert-card-info     { border-left-color: #3B82F6; background: #EFF6FF; }
.alert-severity {
    font-size: 0.75rem;
    font-weight: 700;
    text-transform: uppercase;
}
.alert-message {
    font-size: 0.9rem;
    color: #374151;
    margin: 0.2rem 0;
}
.alert-time {
    font-size: 0.75rem;
    color: #9CA3AF;
}

/* ── Feature cards (landing) ───────────────────── */
.feature-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 12px;
    padding: 2rem 1.5rem;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    height: 100%;
}
.feature-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}
.feature-title {
    font-size: 1.1rem;
    font-weight: 600;
    color: #1A1D29;
    margin-bottom: 0.5rem;
}
.feature-desc {
    font-size: 0.9rem;
    color: #6B7280;
    line-height: 1.5;
}

/* ── Auth form container ───────────────────────── */
.auth-container {
    max-width: 440px;
    margin: 2rem auto;
    padding: 2.5rem;
    background: #FFFFFF;
    border-radius: 16px;
    border: 1px solid #E5E7EB;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
}
.auth-title {
    text-align: center;
    font-size: 1.5rem;
    font-weight: 700;
    color: #1A1D29;
    margin-bottom: 0.5rem;
}
.auth-subtitle {
    text-align: center;
    font-size: 0.9rem;
    color: #6B7280;
    margin-bottom: 1.5rem;
}

/* ── Hero (landing) ────────────────────────────── */
.hero-section {
    text-align: center;
    padding: 3rem 1rem 2rem;
}
.hero-brand {
    font-size: 3rem;
    font-weight: 800;
    color: #0066FF;
    margin-bottom: 0.5rem;
}
.hero-tagline {
    font-size: 1.3rem;
    color: #374151;
    max-width: 550px;
    margin: 0 auto 0.5rem;
    line-height: 1.5;
}
.hero-sub {
    font-size: 1rem;
    color: #6B7280;
    max-width: 500px;
    margin: 0 auto 2rem;
}

/* ── Section headers ───────────────────────────── */
.section-header {
    font-size: 1.15rem;
    font-weight: 600;
    color: #1A1D29;
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 2px solid #E5E7EB;
}

/* ── Misc ──────────────────────────────────────── */
.text-muted { color: #6B7280; font-size: 0.85rem; }
.text-center { text-align: center; }
.mt-1 { margin-top: 0.5rem; }
.mt-2 { margin-top: 1rem; }
.mb-1 { margin-bottom: 0.5rem; }
.mb-2 { margin-bottom: 1rem; }
</style>"""
