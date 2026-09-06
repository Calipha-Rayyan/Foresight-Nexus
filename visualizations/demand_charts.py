import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from visualizations.theme import COLORS

_DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"]


def create_demand_trend_chart(daily: pd.DataFrame, tail_days: int = 365) -> go.Figure:
    fig = px.line(daily.tail(tail_days), x="date", y="demand")
    fig.update_traces(line_color=COLORS["accent"])
    fig.update_layout(height=340, xaxis_title=None, yaxis_title="Demand")
    return fig


def create_weekly_seasonality_chart(df: pd.DataFrame) -> go.Figure:
    dow = df.copy()
    dow["dow"] = dow["date"].dt.day_name()
    wk = dow.groupby("dow")["quantity"].mean().reindex(_DOW_ORDER)
    fig = px.bar(x=wk.index, y=wk.values, labels={"x": "Day of Week", "y": "Avg Demand"})
    fig.update_traces(marker_color=COLORS["accent"])
    fig.update_layout(height=300, title="Weekly Pattern")
    return fig


def create_monthly_seasonality_chart(df: pd.DataFrame) -> go.Figure:
    mo = df.copy()
    mo["month"] = mo["date"].dt.month_name()
    mv = mo.groupby("month")["quantity"].mean().reindex(_MONTH_ORDER).dropna()
    fig = px.bar(x=mv.index, y=mv.values, labels={"x": "Month", "y": "Avg Demand"})
    fig.update_traces(marker_color=COLORS["accent2"])
    fig.update_layout(height=300, title="Monthly Pattern")
    return fig


def create_category_demand_chart(category_totals: pd.DataFrame) -> go.Figure:
    """category_totals: columns [category, total_demand]."""
    cat = category_totals.sort_values("total_demand", ascending=True)
    fig = px.bar(cat, x="total_demand", y="category", orientation="h")
    fig.update_traces(marker_color=COLORS["accent"])
    fig.update_layout(height=320, xaxis_title="Total Demand", yaxis_title=None)
    return fig


def create_revenue_trend_chart(rev: pd.DataFrame) -> go.Figure:
    """rev: columns [date, revenue]."""
    fig = go.Figure(go.Bar(x=rev["date"], y=rev["revenue"], marker_color=COLORS["accent2"]))
    fig.update_layout(height=280, xaxis_title=None, yaxis_title="Revenue")
    return fig
