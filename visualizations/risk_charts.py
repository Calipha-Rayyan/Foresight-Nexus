"""Visualizations for risk distribution and demand anomaly detection."""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from visualizations.validation import validate_chart_df
from core.constants import RISK_COLORS, HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL


def create_risk_distribution_chart(snapshot: pd.DataFrame) -> go.Figure:
    """Shows count of products across health states (Healthy, Watch, At Risk, Critical)."""
    fig = go.Figure()
    if snapshot is None or snapshot.empty or "health" not in snapshot.columns:
        fig.update_layout(title="No risk data", height=280)
        return fig

    order = [HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL]
    counts = snapshot["health"].value_counts().reindex(order).fillna(0)
    bar_colors = [RISK_COLORS.get(k, COLORS["accent"]) for k in counts.index]

    fig.add_trace(go.Bar(
        x=counts.index,
        y=counts.values,
        marker=dict(color=bar_colors),
        hovertemplate="Status: <b>%{x}</b><br>Products: <b>%{y}</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Portfolio Health Breakdown", font=dict(size=13, color=COLORS["text"])),
        height=260,
        xaxis_title=None,
        yaxis_title="Product Count",
    )
    return fig


def create_anomaly_timeline_chart(series: pd.DataFrame, anomalies: pd.DataFrame) -> go.Figure:
    """Timeline comparing daily demand against detected statistical anomalies.
    Does NOT use unified hover mode, ensuring zero 'undefined' outputs.
    """
    fig = go.Figure()
    s_clean = validate_chart_df(series, ["date", "demand"])
    a_clean = validate_chart_df(anomalies, ["date", "demand"])

    if len(s_clean):
        fig.add_trace(go.Scatter(
            x=s_clean["date"],
            y=s_clean["demand"],
            name="Observed Demand",
            mode="lines",
            line=dict(color=COLORS["accent"], width=1.5),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Demand: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    if len(a_clean):
        fig.add_trace(go.Scatter(
            x=a_clean["date"],
            y=a_clean["demand"],
            mode="markers",
            name="Detected Anomaly",
            marker=dict(color=COLORS["critical"], size=10, symbol="x", line=dict(width=2, color="#FFFFFF")),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>⚠️ <b>Statistical Anomaly</b><br>Observed Demand: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Demand History & Outlier Detection", font=dict(size=14, color=COLORS["text"])),
        height=320,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1),
        xaxis_title=None,
        yaxis_title="Units",
    )
    return fig
