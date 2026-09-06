import streamlit as st
from core.state import has_data
from ui.components import empty_state, section_title, kpi_card, render_pill
from visualizations.forecast_charts import create_demand_forecast_chart
from visualizations.inventory_charts import create_current_stock_vs_forecast_chart
from visualizations.demand_charts import create_revenue_trend_chart
from utils.pipeline import get_daily_series, get_forecast, best_model_for_product
from analytics.inventory import build_snapshot
from recommendations.engine import build_recommendation

st.title("Product Explorer")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to explore products.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

product_names = df[["product_id", "product_name"]].drop_duplicates()
label = st.selectbox("Select a product", (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist())
product_id = label.split("(")[-1].rstrip(")")
row = df[df["product_id"] == product_id].sort_values("date").iloc[-1]

st.markdown(f"### {row['product_name']}")
st.caption(f"Category: {row.get('category', 'N/A')}  ·  Product ID: {product_id}")

if not has_inv:
    st.info("No inventory field in this dataset — stock, coverage, and reorder metrics are unavailable. Demand and forecast are still shown below.")

series = get_daily_series(df, product_id)

with st.spinner("Analyzing product..."):
    model_name, reason, _ = best_model_for_product(series, settings)
    fc = get_forecast(series, model_name, 30)

    if has_inv:
        # Same snapshot as every other page — current_stock and lead_time here
        # are guaranteed identical to what Command Center/Alerts/Recommendations show.
        snap_row = build_snapshot(df[df["product_id"] == product_id], settings).iloc[0]
        current_stock = snap_row["current_stock"]
        lead_time = snap_row["lead_time_days"]
        rec = build_recommendation(product_id, row["product_name"], series["demand"], fc, current_stock, lead_time, settings)

if has_inv:
    st.markdown(render_pill(rec.health), unsafe_allow_html=True)
    st.write("")
    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1: kpi_card("Current Stock", f"{current_stock:.0f}")
    with c2: kpi_card("30-Day Forecast", f"{fc['forecast'].sum():,.0f}")
    with c3: kpi_card("Coverage", f"{rec.coverage_days} days" if rec.coverage_days >= 0 else "∞")
    with c4: kpi_card("Reorder Point", f"{rec.reorder_point:.0f}")
    with c5: kpi_card("Safety Stock", f"{rec.safety_stock:.0f}")
    with c6: kpi_card("Recommended Order", f"{rec.recommended_order_qty:.0f}")
    st.info(rec.explanation)
else:
    c1, c2 = st.columns(2)
    with c1: kpi_card("30-Day Forecast", f"{fc['forecast'].sum():,.0f}")
    with c2: kpi_card("Model Used", model_name)

section_title("Demand History & Forecast")
st.plotly_chart(create_demand_forecast_chart(series, fc, history_tail_days=120), use_container_width=True)

if has_inv:
    section_title("Inventory Over Time")
    inv_series = df[df["product_id"] == product_id].sort_values("date").tail(180)
    st.plotly_chart(create_current_stock_vs_forecast_chart(inv_series, rec.reorder_point), use_container_width=True)

if "revenue" in df.columns:
    section_title("Revenue")
    rev = df[df["product_id"] == product_id].sort_values("date").tail(180)
    st.plotly_chart(create_revenue_trend_chart(rev), use_container_width=True)
