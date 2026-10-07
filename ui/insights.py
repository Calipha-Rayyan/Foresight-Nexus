"""Executive summary narratives and automated business insights."""
import streamlit as st


def render_insight_card(
    title: str,
    points: list[str],
    urgency: str = "normal",
) -> None:
    """Renders an executive summary card with structured narrative points."""
    items_html = "".join(f'<li class="fn-insight-item">{p}</li>' for p in points)
    html = (
        f'<div class="fn-card fn-insight-card fn-insight-{urgency}">'
        f'<div class="fn-insight-header">'
        f'<span class="fn-insight-icon">💡</span>'
        f'<h4 class="fn-insight-title">{title}</h4>'
        f'</div>'
        f'<ul class="fn-insight-list">{items_html}</ul>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
