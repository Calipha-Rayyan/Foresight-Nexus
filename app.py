import streamlit as st
from core.config import APP_NAME, APP_TAGLINE
from core.state import init_state
from ui.css import APP_CSS
from ui.branding import render_sidebar_mark, get_favicon

import visualizations.theme as _theme  # noqa: F401 — registers plotly theme on import
try:
    _page_icon = get_favicon()
except Exception:
    _page_icon = "◆"  # never let a favicon/asset problem block app boot

st.set_page_config(page_title=f"{APP_NAME} — AI Demand & Inventory Intelligence",
                    page_icon=_page_icon, layout="wide", initial_sidebar_state="expanded")

st.markdown(APP_CSS, unsafe_allow_html=True)
init_state()

pages = {
    "FORESIGHT Nexus": [
        st.Page("pages/command_center.py", title="Command Center", icon=":material/dashboard:"),
        st.Page("pages/demand_intelligence.py", title="Demand Intelligence", icon=":material/trending_up:"),
        st.Page("pages/inventory_intelligence.py", title="Inventory Intelligence", icon=":material/inventory_2:"),
        st.Page("pages/forecast_studio.py", title="Forecast Studio", icon=":material/insights:"),
        st.Page("pages/product_explorer.py", title="Product Explorer", icon=":material/search:"),
        st.Page("pages/alerts_risks.py", title="Alerts & Risks", icon=":material/warning:"),
        st.Page("pages/recommendations.py", title="Recommendations", icon=":material/checklist:"),
        st.Page("pages/data_lab.py", title="Data Lab", icon=":material/database:"),
        st.Page("pages/model_performance.py", title="Model Performance", icon=":material/analytics:"),
        st.Page("pages/settings.py", title="Settings", icon=":material/tune:"),
    ]
}

with st.sidebar:
    render_sidebar_mark(APP_NAME)
    st.caption(APP_TAGLINE)
    st.divider()

nav = st.navigation(pages)
nav.run()
