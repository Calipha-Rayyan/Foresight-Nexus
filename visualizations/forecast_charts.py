"""Reusable Plotly figure builders for forecast-related charts. Pages collect
data and call these; they never construct go.Figure() directly."""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS


def create_demand_forecast_chart(history: pd.DataFrame, forecast_df: pd.DataFrame,
                                  history_tail_days: int = 120, title: str = None) -> go.Figure:
    """history: [date, demand]. forecast_df: [date, forecast, lower, upper]."""
    fig = go.Figure()
    hist_tail = history.tail(history_tail_days)
    fig.add_trace(go.Scatter(x=hist_tail["date"], y=hist_tail["demand"], name="Historical",
                              line=dict(color=COLORS["accent"], width=2)))
    fig.add_trace(go.Scatter(x=forecast_df["date"], y=forecast_df["forecast"], name="Forecast",
                              line=dict(color=COLORS["accent2"], width=2, dash="dash")))
    fig.add_trace(go.Scatter(
        x=pd.concat([forecast_df["date"], forecast_df["date"][::-1]]),
        y=pd.concat([forecast_df["upper"], forecast_df["lower"][::-1]]),
        fill="toself", fillcolor="rgba(124,108,240,0.15)",
        line=dict(color="rgba(0,0,0,0)"), name="Confidence Interval", hoverinfo="skip"))
    if len(hist_tail):
        fig.add_vline(x=hist_tail["date"].max(), line_dash="dot", line_color=COLORS["text_muted"])
    fig.update_layout(height=380, hovermode="x unified", legend=dict(orientation="h", y=1.12),
                       xaxis_rangeslider_visible=True, title=title)
    return fig


def create_actual_vs_forecast_chart(actual: pd.DataFrame, predicted: pd.DataFrame, title: str = None) -> go.Figure:
    """actual/predicted: [date, demand] over the same backtest window."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=actual["date"], y=actual["demand"], name="Actual",
                              line=dict(color=COLORS["accent"], width=2)))
    fig.add_trace(go.Scatter(x=predicted["date"], y=predicted["demand"], name="Predicted",
                              line=dict(color=COLORS["accent2"], width=2, dash="dot")))
    fig.update_layout(height=320, hovermode="x unified", legend=dict(orientation="h", y=1.12), title=title)
    return fig


def create_forecast_accuracy_chart(comparison_df: pd.DataFrame) -> go.Figure:
    """comparison_df: columns [Model, WAPE (%)] (lower is better)."""
    df = comparison_df.dropna(subset=["WAPE (%)"]).sort_values("WAPE (%)")
    colors = [COLORS["accent"] if i == 0 else COLORS["border"] for i in range(len(df))]
    fig = go.Figure(go.Bar(x=df["WAPE (%)"], y=df["Model"], orientation="h", marker_color=colors))
    fig.update_layout(height=280, xaxis_title="WAPE (%) — lower is better", yaxis_title=None)
    return fig
