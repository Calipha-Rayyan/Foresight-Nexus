"""Typographic hierarchy primitives: page headers and section headers."""
import streamlit as st


def render_page_header(
    title: str,
    subtitle: str | None = None,
    badge: str | None = None,
    meta_items: list[str] | None = None,
) -> None:
    """Renders a SaaS-grade page header with consistent typography."""
    badge_html = f'<div class="fn-page-header-badge">{badge}</div>' if badge else ""
    sub_html = f'<p class="fn-page-header-sub">{subtitle}</p>' if subtitle else ""
    
    meta_html = ""
    if meta_items:
        items_str = "".join(f'<span class="fn-meta-item">{item}</span>' for item in meta_items)
        meta_html = f'<div class="fn-page-header-meta">{items_str}</div>'

    html = (
        f'<div class="fn-page-header">'
        f'<div class="fn-page-header-top">'
        f'<h1 class="fn-page-header-title">{title}</h1>'
        f'{badge_html}'
        f'</div>'
        f'{sub_html}'
        f'{meta_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_section_header(title: str, subtitle: str | None = None) -> None:
    """Renders a section header establishing visual groupings."""
    sub_html = f'<p class="fn-section-sub">{subtitle}</p>' if subtitle else ""
    html = (
        f'<div class="fn-section-wrap">'
        f'<h3 class="fn-section-title">{title}</h3>'
        f'{sub_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def section_title(title: str, subtitle: str | None = None) -> None:
    """Backward-compatible alias for render_section_header."""
    render_section_header(title, subtitle)
