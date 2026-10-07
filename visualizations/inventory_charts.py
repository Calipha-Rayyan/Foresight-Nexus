"""Visualizations for inventory intelligence, stockout risk, and stock aging."""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from visualizations.validation import safe_label, validate_chart_df
from core.constants import RISK_COLORS, HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL


def create_inventory_health_matrix(snapshot: pd.DataFrame) -> go.Figure:
    """Scatter matrix mapping Inventory Level (X) against Daily Demand (Y).
    Grouped by inventory health status with explicit hover cards.
    """
    fig = go.Figure()
    if snapshot is None or snapshot.empty:
        fig.update_layout(title="No inventory snapshot data", height=380)
        return fig

    clean = validate_chart_df(snapshot, ["stock", "avg_daily_demand", "health", "product_name"])

    for health_status in [HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL]:
        subset = clean[clean["health"] == health_status]
        if subset.empty:
            continue
        color = RISK_COLORS.get(health_status, COLORS["accent"])
        fig.add_trace(go.Scatter(
            x=subset["stock"],
            y=subset["avg_daily_demand"],
            mode="markers",
            name=health_status,
            marker=dict(size=10, color=color, opacity=0.85, line=dict(width=1, color="#F1F5F9")),
            customdata=subset[["product_name", "coverage_days"]].values if "coverage_days" in subset.columns else None,
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Current Stock: <b>%{x:,.0f} units</b><br>"
                "Daily Demand: <b>%{y:.1f} units/day</b><br>"
                "Coverage: <b>%{customdata[1]:.1f} days</b><br>"
                "Status: <b>" + health_status + "</b><extra></extra>"
            ) if "coverage_days" in subset.columns else (
                "<b>%{customdata[0]}</b><br>"
                "Current Stock: <b>%{x:,.0f} units</b><br>"
                "Daily Demand: <b>%{y:.1f} units/day</b><extra></extra>"
            ),
        ))

    fig.update_layout(
        title=dict(text="Inventory Health Matrix (Stock vs. Demand Velocity)", font=dict(size=14, color=COLORS["text"])),
        height=380,
        xaxis_title="Current Stock on Hand",
        yaxis_title="Average Daily Demand (units)",
        legend=dict(title=dict(text="Health Status", font=dict(color=COLORS["text_muted"])), orientation="h", y=1.05),
    )
    return fig


def create_stockout_risk_chart(snapshot: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Ranks products with lowest days of stock remaining (highest urgency)."""
    fig = go.Figure()
    if snapshot is None or snapshot.empty or "days_to_stockout" not in snapshot.columns:
        fig.update_layout(title="No stockout risk data", height=280)
        return fig

    # Filter to items with positive/valid days to stockout, sorted most urgent first
    df = snapshot[snapshot["days_to_stockout"] >= 0].sort_values("days_to_stockout", ascending=True).head(top_n)
    if df.empty:
        fig.update_layout(title="No imminent stockouts detected", height=280)
        return fig

    # Invert for horizontal bar display so most urgent is at top
    df = df.iloc[::-1]

    bar_colors = [
        COLORS["critical"] if dts <= 7 else (COLORS["at_risk"] if dts <= 14 else COLORS["watch"])
        for dts in df["days_to_stockout"]
    ]

    # Provide clear text labels and slight visual width for 0-day stockout items
    bar_widths = [max(float(dts), 0.25) if dts == 0 else float(dts) for dts in df["days_to_stockout"]]
    bar_texts = [
        f" 0.0d (OUT OF STOCK)" if dts == 0 else f" {dts:.1f}d"
        for dts in df["days_to_stockout"]
    ]

    fig.add_trace(go.Bar(
        x=bar_widths,
        y=df["product_name"],
        orientation="h",
        text=bar_texts,
        textposition="outside",
        textfont=dict(color=COLORS["text"], size=11),
        marker=dict(color=bar_colors, line=dict(color="rgba(255,255,255,0.15)", width=1)),
        customdata=df["days_to_stockout"],
        hovertemplate="<b>%{y}</b><br>Days to Stockout: <b>%{customdata:.1f} days</b><extra></extra>",
    ))

    max_val = max(df["days_to_stockout"].max(), 5.0)
    fig.update_layout(
        title=dict(text=f"Imminent Stockout Risk (Top {min(top_n, len(df))} Urgent Products)", font=dict(size=13, color=COLORS["text"])),
        height=max(260, 34 * len(df)),
        xaxis=dict(
            title="Estimated Days Until Stockout",
            rangemode="nonnegative",
            range=[0, max_val * 1.25],
        ),
        yaxis_title=None,
    )
    return fig


def create_inventory_aging_chart(aged: pd.DataFrame, value_col: str = "units") -> go.Figure:
    """Displays inventory distributed across coverage aging buckets:
    0–7 days, 8–14 days, 15–30 days, 30+ days.
    """
    fig = go.Figure()
    if aged is None or aged.empty or "age_bucket" not in aged.columns:
        fig.update_layout(title="No aging data", height=280)
        return fig

    colors = [COLORS["critical"], COLORS["watch"], COLORS["healthy"], COLORS["accent2"]]
    fig.add_trace(go.Bar(
        x=aged["age_bucket"],
        y=aged[value_col],
        marker=dict(color=colors[:len(aged)]),
        hovertemplate="Coverage Window: <b>%{x}</b><br>Stock Volume: <b>%{y:,.0f} units</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Inventory Coverage Aging Distribution", font=dict(size=13, color=COLORS["text"])),
        height=300,
        xaxis_title="Stock Coverage Window",
        yaxis_title="Total Units",
    )
    return fig


def create_current_stock_vs_forecast_chart(
    inventory_series: pd.DataFrame,
    reorder_point: float,
    product_name: str | None = None,
) -> go.Figure:
    """Visualizes historic inventory depletion with reorder threshold benchmark."""
    fig = go.Figure()
    inv_clean = validate_chart_df(inventory_series, ["date", "inventory"])

    p_name = safe_label(product_name, default="Product")

    if len(inv_clean):
        fig.add_trace(go.Scatter(
            x=inv_clean["date"],
            y=inv_clean["inventory"],
            name="Inventory on Hand",
            mode="lines",
            line=dict(color=COLORS["accent"], width=2),
            fill="tozeroy",
            fillcolor="rgba(40, 184, 255, 0.08)",
            hovertemplate="<b>%{x|%b %d, %Y}</b><br>Stock: <b>%{y:,.0f} units</b><extra></extra>",
        ))

    fig.add_hline(
        y=reorder_point,
        line_dash="dash",
        line_color=COLORS["watch"],
        line_width=1.5,
        annotation_text=f"Reorder Point ({reorder_point:,.0f} units)",
        annotation_position="top right",
        annotation_font=dict(color=COLORS["watch"], size=11),
    )

    fig.update_layout(
        title=dict(text=f"{p_name} — Inventory Trajectory vs. Reorder Point", font=dict(size=14, color=COLORS["text"])),
        height=300,
        hovermode="closest",
        xaxis_title=None,
        yaxis_title="Units in Stock",
    )
    return fig
