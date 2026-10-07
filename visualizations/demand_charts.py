"""Demand visualizations: trend, weekly/monthly seasonality, and category distribution."""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from visualizations.validation import validate_chart_df

_DOW_ORDER = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
_MONTH_ORDER = ["January", "February", "March", "April", "May", "June", "July",
                "August", "September", "October", "November", "December"]


def create_demand_trend_chart(daily: pd.DataFrame, tail_days: int = 365) -> go.Figure:
    """Historical aggregate demand velocity line chart."""
    fig = go.Figure()
    clean = validate_chart_df(daily, ["date", "demand"])
    clean_tail = clean.tail(tail_days) if len(clean) else clean

    if len(clean_tail):
        fig.add_trace(go.Scatter(
            x=clean_tail["date"],
            y=clean_tail["demand"],
            name="Daily Demand",
            mode="lines",
            line=dict(color=COLORS["accent"], width=2),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Demand: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=f"Daily Demand Trajectory (Last {min(tail_days, len(clean_tail))} Days)", font=dict(size=14, color=COLORS["text"])),
        height=320,
        hovermode="closest",
        xaxis_title=None,
        yaxis_title="Units",
    )
    return fig


def create_weekly_seasonality_chart(df: pd.DataFrame) -> go.Figure:
    """Calculates and visualizes average demand by day of week."""
    fig = go.Figure()
    if df is None or df.empty or "date" not in df.columns or "quantity" not in df.columns:
        fig.update_layout(title="No seasonality data", height=280)
        return fig

    dow = df.copy()
    dow["dow"] = pd.to_datetime(dow["date"]).dt.day_name()
    wk = dow.groupby("dow")["quantity"].mean().reindex(_DOW_ORDER).dropna()

    fig.add_trace(go.Bar(
        x=wk.index,
        y=wk.values,
        marker=dict(color=COLORS["accent"]),
        hovertemplate="Day: <b>%{x}</b><br>Avg Daily Demand: <b>%{y:.1f} units</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Weekly Seasonality Pattern", font=dict(size=13, color=COLORS["text"])),
        height=280,
        xaxis_title=None,
        yaxis_title="Avg Units / Day",
    )
    return fig


def create_monthly_seasonality_chart(df: pd.DataFrame) -> go.Figure:
    """Calculates and visualizes average demand by calendar month."""
    fig = go.Figure()
    if df is None or df.empty or "date" not in df.columns or "quantity" not in df.columns:
        fig.update_layout(title="No monthly data", height=280)
        return fig

    mo = df.copy()
    mo["month"] = pd.to_datetime(mo["date"]).dt.month_name()
    mv = mo.groupby("month")["quantity"].mean().reindex(_MONTH_ORDER).dropna()

    fig.add_trace(go.Bar(
        x=mv.index,
        y=mv.values,
        marker=dict(color=COLORS["accent2"]),
        hovertemplate="Month: <b>%{x}</b><br>Avg Daily Demand: <b>%{y:.1f} units</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Monthly Demand Cycle", font=dict(size=13, color=COLORS["text"])),
        height=280,
        xaxis_title=None,
        yaxis_title="Avg Units / Day",
    )
    return fig


def create_category_demand_chart(category_totals: pd.DataFrame) -> go.Figure:
    """Horizontal bar chart comparing total demand volume across categories."""
    fig = go.Figure()
    if category_totals is None or category_totals.empty:
        fig.update_layout(title="No category demand data", height=280)
        return fig

    cat = category_totals.sort_values("total_demand", ascending=True)

    fig.add_trace(go.Bar(
        x=cat["total_demand"],
        y=cat["category"],
        orientation="h",
        marker=dict(color=COLORS["accent"]),
        hovertemplate="Category: <b>%{y}</b><br>Total Demand: <b>%{x:,.0f} units</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Demand Distribution by Category", font=dict(size=13, color=COLORS["text"])),
        height=max(260, 36 * len(cat)),
        xaxis_title="Total Units Demanded",
        yaxis_title=None,
    )
    return fig


def create_revenue_trend_chart(rev: pd.DataFrame) -> go.Figure:
    """Daily revenue velocity bar chart."""
    fig = go.Figure()
    clean = validate_chart_df(rev, ["date", "revenue"])

    if len(clean):
        fig.add_trace(go.Bar(
            x=clean["date"],
            y=clean["revenue"],
            marker=dict(color=COLORS["accent2"]),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Revenue: <b>$%{y:,.2f}</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text="Revenue Trajectory", font=dict(size=13, color=COLORS["text"])),
        height=280,
        xaxis_title=None,
        yaxis_title="Revenue ($)",
    )
    return fig
