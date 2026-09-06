import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from core.constants import RISK_COLORS


def create_risk_distribution_chart(snapshot: pd.DataFrame) -> go.Figure:
    """snapshot: column [health]. Shows a count of products per health category."""
    counts = snapshot["health"].value_counts().reindex(["Healthy", "Watch", "At Risk", "Critical"]).fillna(0)
    fig = go.Figure(go.Bar(x=counts.index, y=counts.values,
                            marker_color=[RISK_COLORS.get(k, COLORS["accent"]) for k in counts.index]))
    fig.update_layout(height=280, xaxis_title=None, yaxis_title="Products")
    return fig


def create_anomaly_timeline_chart(series: pd.DataFrame, anomalies: pd.DataFrame) -> go.Figure:
    """series: [date, demand]. anomalies: [date, demand, ...] subset flagged as anomalous."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=series["date"], y=series["demand"], name="Demand",
                              line=dict(color=COLORS["accent"], width=1.5)))
    if len(anomalies):
        fig.add_trace(go.Scatter(x=anomalies["date"], y=anomalies["demand"], mode="markers",
                                  name="Anomaly", marker=dict(color=COLORS["critical"], size=9, symbol="x")))
    fig.update_layout(height=320, hovermode="x unified", legend=dict(orientation="h", y=1.12))
    return fig
