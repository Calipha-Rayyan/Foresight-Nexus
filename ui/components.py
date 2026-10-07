"""FORESIGHT Nexus — UI Primitives Facade.

Maintains complete backward compatibility while exposing the full modular design system.
"""
from ui.branding import render_sidebar_brand, render_hero_brand, render_sidebar_mark, get_favicon, load_svg
from ui.status import render_status_badge, render_pill
from ui.headers import render_page_header, render_section_header, section_title
from ui.cards import (
    render_kpi_card, kpi_card,
    render_alert_card, alert_card,
    render_recommendation_card,
    render_forecast_summary_card,
    render_empty_state, empty_state,
    render_hero,
)
from ui.navigation import render_sidebar_status, render_sidebar_footer
from ui.tables import style_dataframe
from ui.insights import render_insight_card
from ui.three_d import render_nexus_visual

__all__ = [
    "render_sidebar_brand",
    "render_hero_brand",
    "render_sidebar_mark",
    "get_favicon",
    "load_svg",
    "render_status_badge",
    "render_pill",
    "render_page_header",
    "render_section_header",
    "section_title",
    "render_kpi_card",
    "kpi_card",
    "render_alert_card",
    "alert_card",
    "render_recommendation_card",
    "render_forecast_summary_card",
    "render_empty_state",
    "empty_state",
    "render_hero",
    "render_sidebar_status",
    "render_sidebar_footer",
    "style_dataframe",
    "render_insight_card",
    "render_nexus_visual",
]
