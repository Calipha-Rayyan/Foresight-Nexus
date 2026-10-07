"""Visualizations for priority inventory reorder recommendations."""
import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS
from visualizations.validation import validate_chart_df


def create_reorder_recommendation_chart(recs: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """Bullet-style horizontal bar chart illustrating highest priority order quantities."""
    fig = go.Figure()
    if recs is None or recs.empty or "recommended_order_qty" not in recs.columns:
        fig.update_layout(title="No reorder recommendations", height=280)
        return fig

    clean = validate_chart_df(recs, ["product_name", "recommended_order_qty"])
    df = clean.sort_values("recommended_order_qty", ascending=True).tail(top_n)

    if df.empty:
        fig.update_layout(title="No pending reorders", height=280)
        return fig

    fig.add_trace(go.Bar(
        x=df["recommended_order_qty"],
        y=df["product_name"],
        orientation="h",
        marker=dict(color=COLORS["accent"], line=dict(color="rgba(255,255,255,0.1)", width=1)),
        hovertemplate="<b>%{y}</b><br>Recommended Order: <b>%{x:,.0f} units</b><extra></extra>",
    ))

    fig.update_layout(
        title=dict(text=f"Priority Replenishment Quantities (Top {len(df)} Items)", font=dict(size=13, color=COLORS["text"])),
        height=max(260, 32 * len(df)),
        xaxis_title="Recommended Purchase Order (Units)",
        yaxis_title=None,
    )
    return fig
