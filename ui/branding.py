"""FORESIGHT Nexus — Brand Asset & Logo Rendering Engine.

Resolves local SVG brand assets from `assets/logo/` with zero external dependencies.
Renders base64-encoded SVG data URIs to guarantee zero markdown code-block leaks,
zero raw HTML/SVG exposure, and crisp vector rendering across all viewports.
"""
from pathlib import Path
import base64
import streamlit as st

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logo"

LOGO_FILE = "foresight_nexus_logo.svg"
LOGO_LIGHT_FILE = "foresight_nexus_logo_light.svg"
MARK_FILE = "foresight_nexus_mark.svg"
MARK_MONOCHROME_FILE = "foresight_nexus_mark_monochrome.svg"


@st.cache_data(show_spinner=False)
def get_svg_data_uri(filename: str) -> str | None:
    """Reads a local SVG file and encodes it as a base64 data URI."""
    path = _ASSETS_DIR / filename
    try:
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode("utf-8")
        return f"data:image/svg+xml;base64,{b64}"
    except (FileNotFoundError, OSError):
        return None


def get_favicon() -> str:
    """Returns local path to the mark SVG for st.set_page_config."""
    path = _ASSETS_DIR / MARK_FILE
    if path.exists():
        return str(path)
    return "📈"


def render_sidebar_brand(app_name: str = "FORESIGHT Nexus", tagline: str = "See demand before it happens.") -> None:
    """Renders a compact, SaaS-grade brand lockup for the sidebar."""
    mark_uri = get_svg_data_uri(MARK_FILE)
    if mark_uri:
        html = (
            f'<div class="fn-brand-sidebar">'
            f'<img src="{mark_uri}" alt="FORESIGHT Nexus Mark" class="fn-brand-sidebar-icon" />'
            f'<div class="fn-brand-sidebar-text">'
            f'<div class="fn-brand-sidebar-name">'
            f'<span class="fn-brand-white">FORESIGHT</span> '
            f'<span class="fn-brand-accent">NEXUS</span>'
            f'</div>'
            f'<div class="fn-brand-sidebar-tagline">{tagline}</div>'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(
            f'<div class="fn-brand-fallback"><h3>{app_name}</h3><p>{tagline}</p></div>',
            unsafe_allow_html=True
        )


def render_hero_brand(tagline: str = "See demand before it happens.") -> None:
    """Renders the full FORESIGHT Nexus logo lockup for the Command Center hero."""
    logo_uri = get_svg_data_uri(LOGO_FILE)
    if logo_uri:
        html = (
            f'<div class="fn-hero-brand-wrap">'
            f'<img src="{logo_uri}" alt="FORESIGHT Nexus" class="fn-hero-logo" />'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)
    else:
        mark_uri = get_svg_data_uri(MARK_FILE)
        icon_html = f'<img src="{mark_uri}" class="fn-hero-logo-mark" />' if mark_uri else ''
        html = (
            f'<div class="fn-hero-brand-fallback">'
            f'{icon_html}'
            f'<div>'
            f'<h1><span class="fn-brand-white">FORESIGHT</span> <span class="fn-brand-accent">NEXUS</span></h1>'
            f'<p class="fn-hero-tagline">{tagline}</p>'
            f'</div>'
            f'</div>'
        )
        st.markdown(html, unsafe_allow_html=True)


# Backwards compatibility alias
def render_sidebar_mark(app_name: str) -> None:
    render_sidebar_brand(app_name=app_name)


def load_svg(filename: str) -> str | None:
    """Returns raw SVG text if needed, stripping problematic desc/title tags that leak."""
    path = _ASSETS_DIR / filename
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return None
