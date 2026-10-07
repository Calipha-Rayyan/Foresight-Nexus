"""Sidebar navigation widgets and system status indicators."""
import streamlit as st
from core.state import has_data


def render_sidebar_status() -> None:
    """Renders active system telemetry and dataset status in the sidebar."""
    if has_data():
        df = st.session_state["dataset"]
        n_prods = df["product_id"].nunique() if "product_id" in df.columns else 0
        n_rows = len(df)
        mode = "Demo Simulation" if st.session_state.get("demo_mode") else "Ingested Pipeline"
        
        html = (
            f'<div class="fn-sidebar-telemetry">'
            f'<div class="fn-telemetry-header">'
            f'<span class="fn-telemetry-dot fn-dot-healthy fn-pulse-live">●</span>'
            f'<span class="fn-telemetry-title">Engine Calibrated</span>'
            f'</div>'
            f'<div class="fn-telemetry-meta">'
            f'<div><span>Data Pipeline:</span> <b>{mode}</b></div>'
            f'<div><span>Monitored Catalog:</span> <b>{n_prods} Active SKUs</b></div>'
            f'<div><span>Historical Series:</span> <b>{n_rows:,} Records</b></div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    else:
        html = (
            f'<div class="fn-sidebar-telemetry fn-telemetry-idle">'
            f'<div class="fn-telemetry-header">'
            f'<span class="fn-telemetry-dot fn-dot-watch">○</span>'
            f'<span class="fn-telemetry-title">Engine Standing By</span>'
            f'</div>'
            f'<div class="fn-telemetry-meta">'
            f'<span>Awaiting data ingestion</span>'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


def render_sidebar_footer() -> None:
    """Renders sleek, unobtrusive sidebar footer."""
    html = (
        f'<div class="fn-sidebar-footer">'
        f'<div class="fn-footer-brand">FORESIGHT Nexus v2.0</div>'
        f'<div class="fn-footer-desc">AI Demand &amp; Inventory Intelligence</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
