"""Loads the FORESIGHT Nexus SVG brand assets from disk using a path resolved
relative to this file (via pathlib), so it works identically on Windows,
Linux, and Streamlit Community Cloud regardless of the process's working
directory. No external network asset is ever fetched.

Asset variants (assets/logo/, see assets/logo/README.txt for provenance):
- foresight_nexus_logo.svg            primary dark-background wordmark — used
                                       for the primary dark-UI presentation
                                       (Command Center hero).
- foresight_nexus_logo_light.svg      light-background wordmark — for any
                                       future light-theme surface or exported
                                       document (not currently used in-app,
                                       since the app theme is dark-only).
- foresight_nexus_mark.svg            primary app/favicon mark — used for
                                       compact contexts: sidebar and favicon.
- foresight_nexus_mark_monochrome.svg monochrome variant — reserved for
                                       contexts where the gradient mark
                                       wouldn't render well (e.g. a plain-text
                                       README badge or print export); not
                                       currently wired into the running app.
"""
from pathlib import Path
import streamlit as st

_ASSETS_DIR = Path(__file__).resolve().parent.parent / "assets" / "logo"

MARK_FILE = "foresight_nexus_mark.svg"
MARK_MONOCHROME_FILE = "foresight_nexus_mark_monochrome.svg"
LOGO_FILE = "foresight_nexus_logo.svg"
LOGO_LIGHT_FILE = "foresight_nexus_logo_light.svg"


@st.cache_data(show_spinner=False)
def load_svg(filename: str) -> str | None:
    """Returns the raw SVG markup for a file in assets/logo/, or None if it's
    missing — callers should fall back gracefully (e.g. to a text wordmark)
    rather than let a missing asset break the page."""
    path = _ASSETS_DIR / filename
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return None


def render_sidebar_mark(app_name: str) -> None:
    """Compact branding for the sidebar: the favicon-style mark at a small
    fixed size next to the wordmark text."""
    mark_svg = load_svg(MARK_FILE)
    if mark_svg:
        st.markdown(f"""
        <style>
        .fn-sidebar-mark svg {{ width: 28px; height: 28px; display: block; }}
        </style>
        <div style="display:flex; align-items:center; gap:0.5rem; margin-bottom:0.2rem;">
            <div class="fn-sidebar-mark">{mark_svg}</div>
            <span style="font-weight:800; font-size:1.05rem; color:#E6E8EF;">{app_name}</span>
        </div>
        """, unsafe_allow_html=True)
    else:
        # Graceful fallback if the asset is ever missing — never break the sidebar.
        st.markdown(f"### {app_name}")


def get_favicon() -> str:
    """Returns a page_icon value for st.set_page_config: the mark SVG's file
    path if it exists (Streamlit resolves a local image path into a browser
    favicon), otherwise a plain emoji so page load never breaks on a missing
    or unsupported asset."""
    path = _ASSETS_DIR / MARK_FILE
    return str(path) if path.exists() else "◆"
