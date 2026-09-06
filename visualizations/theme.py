import plotly.graph_objects as go
import plotly.io as pio

COLORS = {
    "bg": "#0B0E14",
    "surface": "#131722",
    "border": "#232838",
    "text": "#E6E8EF",
    "text_muted": "#8A90A6",
    "accent": "#4FD1E8",
    "accent2": "#7C6CF0",
    "healthy": "#2ecc71",
    "watch": "#f1c40f",
    "at_risk": "#e67e22",
    "critical": "#e74c3c",
}

_template = go.layout.Template()
_template.layout = go.Layout(
    paper_bgcolor=COLORS["bg"],
    plot_bgcolor=COLORS["bg"],
    font=dict(color=COLORS["text"], family="Inter, -apple-system, sans-serif", size=12),
    colorway=[COLORS["accent"], COLORS["accent2"], COLORS["healthy"], COLORS["watch"],
              COLORS["at_risk"], COLORS["critical"]],
    xaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"], linecolor=COLORS["border"]),
    yaxis=dict(gridcolor=COLORS["border"], zerolinecolor=COLORS["border"], linecolor=COLORS["border"]),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
    margin=dict(l=40, r=20, t=40, b=40),
)
pio.templates["foresight"] = _template
pio.templates.default = "foresight"
