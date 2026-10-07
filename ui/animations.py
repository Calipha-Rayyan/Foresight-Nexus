"""Motion language and CSS animation helper primitives.

Restrained, non-blocking motion that communicates hierarchy and feedback.
Zero inline script tags to ensure complete compatibility and zero raw text exposure.
"""
import streamlit as st


def render_page_entrance() -> None:
    """Injects lightweight keyframe animations for page content reveal."""
    pass  # Handled natively in ui/css.py via .block-container and component classes
