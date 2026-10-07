"""Reusable card primitives: KPI cards, alert cards, recommendation cards,
forecast summary cards, data health scorecards, and empty/loading states.
"""
import streamlit as st
from ui.status import render_status_badge
from ui.branding import render_hero_brand, get_svg_data_uri, MARK_FILE
from core.config import APP_TAGLINE


def render_kpi_card(
    label: str,
    value: str,
    delta: str | None = None,
    delta_positive: bool = True,
    context: str | None = None,
    status: str | None = None,
) -> None:
    """Enterprise KPI card:
    - Dominant primary metric
    - Clear micro-label
    - Trend indicator (up/down arrow)
    - Contextual subtitle
    """
    delta_html = ""
    if delta:
        arrow = "↑" if delta_positive else "↓"
        cls = "fn-kpi-delta-up" if delta_positive else "fn-kpi-delta-down"
        delta_html = f'<div class="{cls}">{arrow} {delta}</div>'

    status_html = f'<div class="fn-kpi-status">{render_status_badge(status)}</div>' if status else ""
    ctx_html = f'<div class="fn-kpi-context">{context}</div>' if context else ""

    html = (
        f'<div class="fn-card fn-kpi-card">'
        f'<div class="fn-kpi-header">'
        f'<span class="fn-kpi-label">{label}</span>'
        f'{status_html}'
        f'</div>'
        f'<div class="fn-kpi-value">{value}</div>'
        f'<div class="fn-kpi-footer">'
        f'{delta_html}'
        f'{ctx_html}'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def kpi_card(label: str, value: str, delta: str | None = None, delta_positive: bool = True, context: str | None = None) -> None:
    """Backward-compatible alias for render_kpi_card."""
    render_kpi_card(label, value, delta=delta, delta_positive=delta_positive, context=context)


def render_alert_card(
    title: str,
    body: str,
    action: str,
    severity: str = "critical",
    category: str | None = None,
    impact: str | None = None,
) -> None:
    """Actionable alert card featuring semantic urgency border, condition, and recommended action."""
    cat_html = f'<span class="fn-alert-category">{category}</span>' if category else ""
    impact_html = f'<div class="fn-alert-impact"><b>Impact:</b> {impact}</div>' if impact else ""
    badge_html = render_status_badge(severity.title())

    html = (
        f'<div class="fn-alert fn-alert-{severity.lower()}">'
        f'<div class="fn-alert-top">'
        f'<div class="fn-alert-header">'
        f'{badge_html}'
        f'<span class="fn-alert-title">{title}</span>'
        f'</div>'
        f'{cat_html}'
        f'</div>'
        f'<div class="fn-alert-body">{body}</div>'
        f'{impact_html}'
        f'<div class="fn-alert-action">'
        f'<span class="fn-alert-action-label">Action Required:</span> {action}'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def alert_card(title: str, body: str, action: str, severity: str = "critical") -> None:
    """Backward-compatible alias for render_alert_card."""
    render_alert_card(title, body, action, severity=severity)


def render_recommendation_card(
    product_name: str,
    risk_level: str,
    current_stock: float,
    expected_demand: float,
    safety_stock: float,
    reorder_point: float,
    recommended_order_qty: float,
    why_reason: str,
) -> None:
    """Decision-oriented replenishment card with dominant order quantity callout."""
    badge_html = render_status_badge(risk_level)
    html = (
        f'<div class="fn-card fn-recommendation-card">'
        f'<div class="fn-rec-header">'
        f'<div class="fn-rec-title-group">'
        f'<h4 class="fn-rec-product-name">{product_name}</h4>'
        f'{badge_html}'
        f'</div>'
        f'<div class="fn-rec-order-badge">'
        f'<span class="fn-rec-order-label">RECOMMENDED ORDER</span>'
        f'<span class="fn-rec-order-val">{recommended_order_qty:,.0f} units</span>'
        f'</div>'
        f'</div>'
        f'<div class="fn-rec-metrics-grid">'
        f'<div class="fn-rec-metric"><span>Current Stock</span><b>{current_stock:,.0f}</b></div>'
        f'<div class="fn-rec-metric"><span>Expected Demand</span><b>{expected_demand:,.0f}</b></div>'
        f'<div class="fn-rec-metric"><span>Safety Stock</span><b>{safety_stock:,.0f}</b></div>'
        f'<div class="fn-rec-metric"><span>Reorder Point</span><b>{reorder_point:,.0f}</b></div>'
        f'</div>'
        f'<div class="fn-rec-why">'
        f'<span class="fn-rec-why-label">Decision Rationale:</span> {why_reason}'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_forecast_summary_card(
    model_name: str,
    forecast_units: float,
    expected_range: str,
    confidence: str,
    reason: str | None = None,
) -> None:
    """Displays key analytical output of the selected forecast model."""
    reason_html = f'<div class="fn-fc-summary-reason"><b>Model Rationale:</b> {reason}</div>' if reason else ""
    html = (
        f'<div class="fn-card fn-forecast-summary-card">'
        f'<div class="fn-fc-summary-grid">'
        f'<div class="fn-fc-item">'
        f'<span class="fn-fc-label">Selected Model</span>'
        f'<span class="fn-fc-val fn-brand-accent">{model_name}</span>'
        f'</div>'
        f'<div class="fn-fc-item">'
        f'<span class="fn-fc-label">Forecast Horizon Total</span>'
        f'<span class="fn-fc-val">{forecast_units:,.0f} units</span>'
        f'</div>'
        f'<div class="fn-fc-item">'
        f'<span class="fn-fc-label">Expected Range (80% CI)</span>'
        f'<span class="fn-fc-val">{expected_range} units</span>'
        f'</div>'
        f'<div class="fn-fc-item">'
        f'<span class="fn-fc-label">Forecast Confidence</span>'
        f'<span class="fn-fc-val">{render_status_badge(confidence)}</span>'
        f'</div>'
        f'</div>'
        f'{reason_html}'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)


def render_empty_state(
    title: str,
    body: str,
    button_label: str | None = None,
    target_page: str | None = None,
) -> None:
    """Enterprise empty state container."""
    btn_html = ""
    html = (
        f'<div class="fn-empty">'
        f'<div class="fn-empty-icon">📊</div>'
        f'<h3 class="fn-empty-title">{title}</h3>'
        f'<p class="fn-empty-body">{body}</p>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if button_label and target_page:
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            if st.button(button_label, type="primary", use_container_width=True):
                st.switch_page(target_page)


def empty_state(title: str, body: str) -> None:
    """Backward-compatible alias for render_empty_state."""
    render_empty_state(title, body)


def render_hero(status_text: str, data_updated: str, model_status: str, show_visual: bool = True) -> None:
    """Hero section for Command Center with Data Nexus visual."""
    status_dot = "●" if "Active" in status_text or "Ready" in status_text else "○"
    status_cls = "fn-dot-healthy" if "Active" in status_text or "Ready" in status_text else "fn-dot-watch"
    mark_uri = get_svg_data_uri(MARK_FILE)
    mark_img = f'<img src="{mark_uri}" class="fn-hero-brand-mark" alt="FORESIGHT Nexus" />' if mark_uri else ""
    
    dataset_label = "Demo Dataset" if st.session_state.get("demo_mode", True) else "Enterprise Ingestion"
    html = (
        f'<div class="fn-hero">'
        f'<div class="fn-hero-content">'
        f'<div class="fn-hero-brand-line">'
        f'{mark_img}'
        f'<span class="fn-hero-title-main">FORESIGHT</span>'
        f'<span class="fn-hero-title-accent">NEXUS</span>'
        f'<span class="fn-hero-pill"><span class="{status_cls}">{status_dot}</span> {status_text}</span>'
        f'</div>'
        f'<p class="fn-hero-tagline">{APP_TAGLINE}</p>'
        f'<p class="fn-hero-desc">Transform demand velocity and inventory signals into automated forecasts and proactive replenishment decisions.</p>'
        f'<div class="fn-hero-meta">'
        f'<span><b>Dataset:</b> {dataset_label}</span>'
        f'<span><b>Last Updated:</b> {data_updated}</span>'
        f'<span><b>Model Status:</b> {model_status}</span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(html, unsafe_allow_html=True)
    if show_visual:
        try:
            from ui.three_d import render_nexus_visual
            render_nexus_visual(height=170)
        except Exception:
            pass
