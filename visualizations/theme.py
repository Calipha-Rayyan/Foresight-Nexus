"""FORESIGHT Nexus — Central Plotly Theme and Semantic Color System.

All charts across the platform inherit this theme to guarantee unified typography,
gridlines, margins, hover labels, and semantic color logic.
"""
import plotly.graph_objects as go
import plotly.io as pio

COLORS = {
    # Core Surfaces
    "bg": "#080B11",
    "surface": "#111622",
    "surface_elevated": "#161D2B",
    "border": "#1F293D",
    
    # Typography
    "text": "#F1F5F9",
    "text_muted": "#8B9BB4",
    
    # Brand Accents
    "accent": "#28B8FF",       # Electric Cyan (prediction / future visibility)
    "accent2": "#8A63FF",      # Restrained Violet (connected intelligence)
    "accent_blue": "#1E5EFF",  # Deep Signal Blue
    
    # Semantic Status
    "healthy": "#10B981",      # Emerald Green (optimal stock / healthy demand)
    "watch": "#F59E0B",        # Amber Yellow (monitor threshold)
    "at_risk": "#F97316",      # Bright Orange (high risk)
    "critical": "#EF4444",     # Crimson Red (urgent stockout / action needed)
}

_template = go.layout.Template()
_template.layout = go.Layout(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["bg"],
    font=dict(
        color=COLORS["text"],
        family="Inter, -apple-system, BlinkMacSystemFont, Segoe UI, Roboto, sans-serif",
        size=12
    ),
    colorway=[
        COLORS["accent"],
        COLORS["accent2"],
        COLORS["healthy"],
        COLORS["watch"],
        COLORS["at_risk"],
        COLORS["critical"],
    ],
    xaxis=dict(
        gridcolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"], size=11),
        title_font=dict(color=COLORS["text"], size=12),
    ),
    yaxis=dict(
        gridcolor=COLORS["border"],
        zerolinecolor=COLORS["border"],
        linecolor=COLORS["border"],
        tickfont=dict(color=COLORS["text_muted"], size=11),
        title_font=dict(color=COLORS["text"], size=12),
    ),
    hoverlabel=dict(
        bgcolor=COLORS["surface"],
        bordercolor=COLORS["accent"],
        font=dict(
            family="Inter, -apple-system, sans-serif",
            color=COLORS["text"],
            size=12
        ),
    ),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        font=dict(color=COLORS["text_muted"], size=11),
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
    ),
    margin=dict(l=48, r=24, t=48, b=40),
)

pio.templates["foresight"] = _template
pio.templates.default = "foresight"

CHART_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}
