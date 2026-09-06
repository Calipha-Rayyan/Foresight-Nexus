import pandas as pd
import plotly.graph_objects as go
from visualizations.theme import COLORS


def create_reorder_recommendation_chart(recs: pd.DataFrame, top_n: int = 12) -> go.Figure:
    """recs: columns [product_name, recommended_order_qty]. Bullet-style horizontal bars,
    highest recommended quantity first."""
    df = recs.sort_values("recommended_order_qty", ascending=True).tail(top_n)
    fig = go.Figure(go.Bar(x=df["recommended_order_qty"], y=df["product_name"], orientation="h",
                            marker_color=COLORS["accent2"]))
    fig.update_layout(height=max(280, 28 * len(df)), xaxis_title="Recommended Order Qty", yaxis_title=None)
    return fig
