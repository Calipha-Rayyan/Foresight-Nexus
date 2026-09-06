import streamlit as st
from core.config import APP_NAME, APP_TAGLINE
from core.constants import (HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL,
                             RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW)

_PILL_CLASS = {
    HEALTH_HEALTHY: "fn-pill-healthy", HEALTH_WATCH: "fn-pill-watch",
    HEALTH_AT_RISK: "fn-pill-risk", HEALTH_CRITICAL: "fn-pill-critical",
    RISK_LOW: "fn-pill-healthy", RISK_MEDIUM: "fn-pill-watch",
    RISK_HIGH: "fn-pill-risk", RISK_CRITICAL: "fn-pill-critical",
}
_PILL_ICON = {
    HEALTH_HEALTHY: "🟢", HEALTH_WATCH: "🟡", HEALTH_AT_RISK: "🟠", HEALTH_CRITICAL: "🔴",
    RISK_LOW: "🟢", RISK_MEDIUM: "🟡", RISK_HIGH: "🟠", RISK_CRITICAL: "🔴",
}


def render_hero(status_text: str, data_updated: str, model_status: str, show_visual: bool = True):
    # Primary dark-UI branding: the full logo asset where available, falling
    # back to the plain text title so the hero never breaks if the SVG asset
    # is ever missing or renamed. Built as one markdown call (not split
    # across two st.markdown calls) so the .fn-hero div nests correctly.
    from ui.branding import load_svg, LOGO_FILE
    logo_svg = load_svg(LOGO_FILE)
    title_html = f'<div style="max-width:380px;">{logo_svg}</div>' if logo_svg else f"<h1>{APP_NAME}</h1>"

    st.markdown(f"""
    <div class="fn-hero">
        {title_html}
        <p class="tagline">{APP_TAGLINE}</p>
        <p class="sub">Transform historical demand and inventory signals into actionable forecasts and replenishment decisions.</p>
        <div class="fn-status">
            <span><span class="dot">●</span> {status_text}</span>
            <span>Data Updated: {data_updated}</span>
            <span>Model Status: {model_status}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    if show_visual:
        # Optional decorative visual — wrapped so a failure here can never
        # break the rest of the page.
        try:
            from ui.three_d import render_nexus_visual
            render_nexus_visual(height=160)
        except Exception:
            pass


def render_pill(label: str) -> str:
    cls = _PILL_CLASS.get(label, "fn-pill-watch")
    icon = _PILL_ICON.get(label, "⚪")
    return f'<span class="fn-pill {cls}">{icon} {label}</span>'


def kpi_card(label: str, value: str, delta: str = None, delta_positive: bool = True, context: str = None):
    delta_html = ""
    if delta:
        cls = "fn-kpi-delta-up" if delta_positive else "fn-kpi-delta-down"
        arrow = "↑" if delta_positive else "↓"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'
    ctx_html = f'<div class="fn-kpi-context">{context}</div>' if context else ""
    st.markdown(f"""
    <div class="fn-card">
        <div class="fn-kpi-label">{label}</div>
        <div class="fn-kpi-value">{value}</div>
        {delta_html}
        {ctx_html}
    </div>
    """, unsafe_allow_html=True)


def alert_card(title: str, body: str, action: str, severity: str = "critical"):
    st.markdown(f"""
    <div class="fn-alert {severity.lower()}">
        <div class="fn-alert-title">{render_pill(severity)} &nbsp; {title}</div>
        <div class="fn-alert-body">{body}</div>
        <div class="fn-alert-action">Recommended action: {action}</div>
    </div>
    """, unsafe_allow_html=True)


def empty_state(title: str, body: str):
    st.markdown(f"""
    <div class="fn-empty">
        <h3>{title}</h3>
        <p>{body}</p>
    </div>
    """, unsafe_allow_html=True)


def section_title(title: str, subtitle: str = None):
    st.markdown(f'<div class="fn-section-title">{title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="fn-section-sub">{subtitle}</div>', unsafe_allow_html=True)
