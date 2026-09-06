"""Lightweight 3D-feeling hero visual: floating data nodes connected to a
central intelligence core, built as pure SVG + CSS animation so it has zero
external dependency and can never break the rest of the app if it fails to
render. No Three.js/Spline dependency is required — this keeps Streamlit
Community Cloud deployment lightweight, per the 'optional, must not block
critical UI' requirement.
"""
import streamlit as st
import random

_NODE_COLORS = ["#4FD1E8", "#7C6CF0", "#4FD1E8", "#39E6C4"]


def render_nexus_visual(height: int = 220, seed: int = 7):
    """Renders a small animated 'data nexus' — a core node with orbiting
    demand-signal nodes and connecting lines. Purely decorative; the app
    functions identically with or without it."""
    try:
        rng = random.Random(seed)
        n_nodes = 7
        cx, cy = 300, height // 2
        nodes = []
        for i in range(n_nodes):
            angle = (360 / n_nodes) * i
            radius = rng.randint(90, 140)
            nodes.append((angle, radius, rng.uniform(0, 3)))

        lines = ""
        dots = ""
        for i, (angle, radius, delay) in enumerate(nodes):
            import math
            rad = math.radians(angle)
            x = cx + radius * math.cos(rad)
            y = cy + radius * math.sin(rad) * 0.5
            color = _NODE_COLORS[i % len(_NODE_COLORS)]
            lines += (f'<line x1="{cx}" y1="{cy}" x2="{x:.0f}" y2="{y:.0f}" '
                      f'stroke="{color}" stroke-opacity="0.25" stroke-width="1">'
                      f'<animate attributeName="stroke-opacity" values="0.1;0.4;0.1" '
                      f'dur="{3+delay:.1f}s" repeatCount="indefinite"/></line>')
            dots += (f'<circle cx="{x:.0f}" cy="{y:.0f}" r="4" fill="{color}">'
                     f'<animate attributeName="r" values="3;5;3" dur="{2+delay:.1f}s" '
                     f'repeatCount="indefinite"/></circle>')

        svg = f"""
        <div style="width:100%;display:flex;justify-content:center;opacity:0.9;">
        <svg viewBox="0 0 600 {height}" width="100%" style="max-width:620px;">
            {lines}
            {dots}
            <circle cx="{cx}" cy="{cy}" r="16" fill="#4FD1E8">
                <animate attributeName="r" values="14;18;14" dur="2.4s" repeatCount="indefinite"/>
            </circle>
            <circle cx="{cx}" cy="{cy}" r="26" fill="none" stroke="#4FD1E8" stroke-width="1" stroke-opacity="0.4">
                <animate attributeName="r" values="22;32;22" dur="2.4s" repeatCount="indefinite"/>
                <animate attributeName="stroke-opacity" values="0.5;0;0.5" dur="2.4s" repeatCount="indefinite"/>
            </circle>
        </svg>
        </div>
        """
        st.markdown(svg, unsafe_allow_html=True)
    except Exception:
        # Graceful fallback — the app must work perfectly even if this fails.
        pass
