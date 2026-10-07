"""Reusable Plotly figure builders for forecast visualizations.

Features visual distinction between historical and predicted demand,
safe hover templates with zero undefined/null values, and responsive layouts.
"""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from visualizations.validation import safe_product_name, safe_label, safe_date, validate_chart_df


def create_demand_forecast_chart(
    history: pd.DataFrame,
    forecast_df: pd.DataFrame,
    product_name: str | None = None,
    history_tail_days: int = 120,
    title: str | None = None,
) -> go.Figure:
    """Hero demand forecast visualization.
    Visual Distinction:
    - Historical: Solid muted line
    - Forecast: Electric cyan dashed line
    - Confidence Interval: Subtle shaded band
    - Forecast Transition: Vertical marker line
    """
    fig = go.Figure()

    # Validate inputs
    hist_clean = validate_chart_df(history, ["date", "demand"])
    fc_clean = validate_chart_df(forecast_df, ["date", "forecast"])

    hist_tail = hist_clean.tail(history_tail_days) if len(hist_clean) else hist_clean

    # Determine Title
    clean_prod = safe_product_name(product_name, default="Aggregate Demand")
    horizon_days = len(fc_clean)
    default_title = f"{clean_prod} — {horizon_days}-Day Demand Forecast" if horizon_days > 0 else f"{clean_prod} — Demand Trend"
    final_title = safe_label(title, default=default_title)

    # 1. Historical Demand Trace
    if len(hist_tail):
        fig.add_trace(go.Scatter(
            x=hist_tail["date"],
            y=hist_tail["demand"],
            name="Historical Demand",
            mode="lines",
            line=dict(color="#94A3B8", width=2),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Historical Demand: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    # 2. Forecast Demand Trace
    if len(fc_clean):
        fig.add_trace(go.Scatter(
            x=fc_clean["date"],
            y=fc_clean["forecast"],
            name="Forecast Demand",
            mode="lines+markers",
            marker=dict(size=4, color=COLORS["accent"]),
            line=dict(color=COLORS["accent"], width=2.5, dash="dash"),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Forecast: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    # 3. Confidence Interval (Upper & Lower Bounds)
    has_bounds = "upper" in fc_clean.columns and "lower" in fc_clean.columns and len(fc_clean) > 0
    if has_bounds:
        fig.add_trace(go.Scatter(
            x=pd.concat([fc_clean["date"], fc_clean["date"][::-1]]),
            y=pd.concat([fc_clean["upper"], fc_clean["lower"][::-1]]),
            fill="toself",
            fillcolor="rgba(40, 184, 255, 0.12)",
            line=dict(color="rgba(0,0,0,0)"),
            name="80% Confidence Interval",
            hoverinfo="skip",
        ))

    # 4. Vertical Forecast Boundary Marker
    if len(hist_tail) and len(fc_clean):
        boundary_date = hist_tail["date"].max()
        fig.add_vline(
            x=boundary_date,
            line_dash="dot",
            line_color=COLORS["text_muted"],
            line_width=1.5,
            annotation_text="Forecast Start",
            annotation_position="top left",
            annotation_font=dict(color=COLORS["text_muted"], size=10),
        )

    fig.update_layout(
        title=dict(text=final_title, font=dict(size=15, color=COLORS["text"])),
        height=380,
        hovermode="closest",  # Never use "x unified" here to prevent 'undefined' on disjoint dates
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1),
        xaxis=dict(title=None, rangeslider=dict(visible=False)),
        yaxis=dict(title="Units Demanded"),
    )
    return fig


def create_actual_vs_forecast_chart(
    actual: pd.DataFrame,
    predicted: pd.DataFrame,
    title: str | None = None,
) -> go.Figure:
    """Evaluates backtest accuracy by comparing held-out actuals against model predictions."""
    fig = go.Figure()
    act_clean = validate_chart_df(actual, ["date", "demand"])
    pred_clean = validate_chart_df(predicted, ["date", "demand"])

    final_title = safe_label(title, default="Actual vs. Predicted (Held-Out Evaluation Window)")

    if len(act_clean):
        fig.add_trace(go.Scatter(
            x=act_clean["date"],
            y=act_clean["demand"],
            name="Actual Demand",
            mode="lines",
            line=dict(color="#94A3B8", width=2),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Actual: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    if len(pred_clean):
        fig.add_trace(go.Scatter(
            x=pred_clean["date"],
            y=pred_clean["demand"],
            name="Predicted Demand",
            mode="lines",
            line=dict(color=COLORS["accent"], width=2.5, dash="dot"),
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Predicted: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    fig.update_layout(
        title=dict(text=final_title, font=dict(size=14, color=COLORS["text"])),
        height=320,
        hovermode="closest",
        legend=dict(orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1),
        xaxis=dict(title=None),
        yaxis=dict(title="Units"),
    )
    return fig


def create_forecast_accuracy_chart(comparison_df: pd.DataFrame) -> go.Figure:
    """Ranks forecasting models by WAPE (Weighted Absolute Percentage Error). Lower is better."""
    fig = go.Figure()
    if comparison_df is None or comparison_df.empty or "WAPE (%)" not in comparison_df.columns:
        fig.update_layout(title="No model evaluation data available", height=280)
        return fig

    df = comparison_df.dropna(subset=["WAPE (%)"]).sort_values("WAPE (%)", ascending=True)
    if df.empty:
        fig.update_layout(title="No evaluation data", height=280)
        return fig

    # Highlight winner in cyan, runners-up in deep slate/border
    colors = [COLORS["accent"] if i == 0 else COLORS["surface_elevated"] for i in range(len(df))]
    border_colors = [COLORS["accent"] if i == 0 else COLORS["border"] for i in range(len(df))]

    # Resolve model column dynamically
    model_col = "Model" if "Model" in df.columns else ("Architecture" if "Architecture" in df.columns else df.columns[0])

    fig.add_trace(go.Bar(
        x=df["WAPE (%)"],
        y=df[model_col],
        orientation="h",
        marker=dict(color=colors, line=dict(color=border_colors, width=1.5)),
        hovertemplate="<b>%{y}</b><br>Backtest WAPE: <b>%{x:.1f}%</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Model Evaluation: WAPE (Lower is Better)", font=dict(size=13, color=COLORS["text"])),
        height=max(260, 36 * len(df)),
        xaxis_title="Backtest Error Rate (%)",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
    )
    return fig
