"""Semantic status badges, pills, and health indicator primitives."""
from core.constants import (
    HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL,
    RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW,
)

_STATUS_CLASSES = {
    HEALTH_HEALTHY: "fn-pill-healthy",
    HEALTH_WATCH: "fn-pill-watch",
    HEALTH_AT_RISK: "fn-pill-risk",
    HEALTH_CRITICAL: "fn-pill-critical",
    RISK_LOW: "fn-pill-healthy",
    RISK_MEDIUM: "fn-pill-watch",
    RISK_HIGH: "fn-pill-risk",
    RISK_CRITICAL: "fn-pill-critical",
    "Active": "fn-pill-healthy",
    "Validated": "fn-pill-healthy",
    "Idle": "fn-pill-watch",
    "Unavailable": "fn-pill-muted",
}

_STATUS_ICONS = {
    HEALTH_HEALTHY: "●",
    HEALTH_WATCH: "●",
    HEALTH_AT_RISK: "●",
    HEALTH_CRITICAL: "●",
    RISK_LOW: "●",
    RISK_MEDIUM: "●",
    RISK_HIGH: "●",
    RISK_CRITICAL: "●",
    "Active": "●",
    "Validated": "✓",
    "Idle": "○",
    "Unavailable": "—",
}


def render_status_badge(label: str, icon: str | None = None) -> str:
    """Returns HTML for a semantic status badge."""
    cls = _STATUS_CLASSES.get(label, "fn-pill-muted")
    dot = icon if icon is not None else _STATUS_ICONS.get(label, "●")
    return f'<span class="fn-pill {cls}"><span class="fn-pill-dot">{dot}</span> {label}</span>'


def render_pill(label: str) -> str:
    """Backward-compatible alias for render_status_badge."""
    return render_status_badge(label)
