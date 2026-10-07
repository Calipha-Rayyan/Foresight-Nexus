import streamlit as st
from core.config import APP_NAME, APP_TAGLINE
from core.state import init_state
from ui.css import APP_CSS
from ui.branding import render_sidebar_brand, get_favicon
from ui.navigation import render_sidebar_status, render_sidebar_footer

import visualizations.theme as _theme  # noqa: F401 — registers central plotly theme on import

try:
    _page_icon = get_favicon()
except Exception:
    _page_icon = "📈"

st.set_page_config(
    page_title=f"{APP_NAME} — AI Demand & Inventory Intelligence",
    page_icon=_page_icon,
    layout="wide",
    initial_sidebar_state="auto",
)

st.markdown(APP_CSS, unsafe_allow_html=True)
init_state()

# Native structured brand logo lockup for sidebar (full logo when open, mark when collapsed)
try:
    st.logo("assets/logo/foresight_nexus_logo.svg", icon_image="assets/logo/foresight_nexus_mark.svg", size="large")
except Exception:
    pass

pages = [
    st.Page("pages/command_center.py", title="Command Center", icon=":material/dashboard:", default=True, url_path=""),
    st.Page("pages/demand_intelligence.py", title="Demand Intelligence", icon=":material/trending_up:", url_path="demand_intelligence"),
    st.Page("pages/inventory_intelligence.py", title="Inventory Intelligence", icon=":material/inventory_2:", url_path="inventory_intelligence"),
    st.Page("pages/forecast_studio.py", title="Forecast Studio", icon=":material/insights:", url_path="forecast_studio"),
    st.Page("pages/product_explorer.py", title="Product Explorer", icon=":material/search:", url_path="product_explorer"),
    st.Page("pages/alerts_risks.py", title="Alerts & Risks", icon=":material/warning:", url_path="alerts_risks"),
    st.Page("pages/recommendations.py", title="Recommendations", icon=":material/checklist:", url_path="recommendations"),
    st.Page("pages/data_lab.py", title="Data Lab", icon=":material/database:", url_path="data_lab"),
    st.Page("pages/model_performance.py", title="Model Performance", icon=":material/analytics:", url_path="model_performance"),
    st.Page("pages/settings.py", title="Settings", icon=":material/tune:", url_path="settings"),
]

nav = st.navigation(pages)
nav.run()

with st.sidebar:
    render_sidebar_status()
    render_sidebar_footer()
