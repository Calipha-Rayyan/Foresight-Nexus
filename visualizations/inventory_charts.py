import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from visualizations.theme import COLORS
from core.constants import RISK_COLORS


def create_inventory_health_matrix(snapshot: pd.DataFrame) -> go.Figure:
    """snapshot: columns [stock, avg_daily_demand, health, product_name, coverage_days]."""
    fig = px.scatter(snapshot, x="stock", y="avg_daily_demand", color="health",
                      hover_data=["product_name", "coverage_days"], color_discrete_map=RISK_COLORS,
                      labels={"stock": "Inventory Level", "avg_daily_demand": "Demand Level"})
    fig.update_layout(height=420, legend_title="Health")
    return fig


def create_inventory_aging_chart(aged: pd.DataFrame, value_col: str = "units") -> go.Figure:
    """aged: columns [age_bucket, <value_col>]."""
    fig = px.bar(aged, x="age_bucket", y=value_col,
                 labels={"age_bucket": "Coverage Bucket", value_col: value_col.title()})
    fig.update_traces(marker_color=COLORS["accent"])
    fig.update_layout(height=300)
    return fig


def create_current_stock_vs_forecast_chart(inventory_series: pd.DataFrame, reorder_point: float) -> go.Figure:
    """inventory_series: [date, inventory]."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=inventory_series["date"], y=inventory_series["inventory"], name="Inventory",
                              line=dict(color=COLORS["accent"]), fill="tozeroy",
                              fillcolor="rgba(79,209,232,0.08)"))
    fig.add_hline(y=reorder_point, line_dash="dot", line_color=COLORS["watch"], annotation_text="Reorder Point")
    fig.update_layout(height=300)
    return fig


def create_stockout_risk_chart(snapshot: pd.DataFrame, top_n: int = 10) -> go.Figure:
    """snapshot: columns [product_name, days_to_stockout]. Shows most urgent first."""
    df = snapshot[snapshot["days_to_stockout"] >= 0].sort_values("days_to_stockout").head(top_n)
    fig = go.Figure(go.Bar(x=df["days_to_stockout"], y=df["product_name"], orientation="h",
                            marker_color=COLORS["critical"]))
    fig.update_layout(height=max(280, 28 * len(df)), xaxis_title="Days to Stockout", yaxis_title=None)
    return fig
