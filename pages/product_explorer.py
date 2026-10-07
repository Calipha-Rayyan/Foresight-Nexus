"""FORESIGHT Nexus — Product Intelligence Profile.

Comprehensive 360-degree analytical profile for individual SKUs, combining demand velocity,
inventory depletion, machine learning forecasts, and replenishment parameters.
"""
import streamlit as st
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_kpi_card, render_recommendation_card, render_empty_state
from ui.status import render_status_badge
from visualizations.forecast_charts import create_demand_forecast_chart
from visualizations.inventory_charts import create_current_stock_vs_forecast_chart
from visualizations.demand_charts import create_revenue_trend_chart
from utils.pipeline import get_daily_series, get_forecast, best_model_for_product
from analytics.inventory import build_snapshot
from recommendations.engine import build_recommendation

render_page_header(
    "Product Explorer",
    "Individual SKU intelligence profile: demand patterns, stock velocity, and replenishment parameters.",
    meta_items=["Single-SKU Telemetry", "Safety Stock Sizing", "Trajectory Analytics"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset",
        "Upload sales history in Data Lab or load the demo dataset to explore individual products.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

# Product Selection Bar
col_sel1, col_sel2 = st.columns([1.5, 3.5])
with col_sel1:
    categories = ["All Categories"] + sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else ["All Categories"]
    selected_cat = st.selectbox("Filter Category", categories)

prod_pool = df if selected_cat == "All Categories" or "category" not in df.columns else df[df["category"] == selected_cat]
vol = prod_pool.groupby("product_id")["quantity"].sum()
product_names = prod_pool[["product_id", "product_name"]].drop_duplicates().copy()
product_names["vol"] = product_names["product_id"].map(vol).fillna(0)
product_names = product_names.sort_values("vol", ascending=False)

with col_sel2:
    prod_options = (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist()
    label = st.selectbox("Select Target Product", prod_options)

product_id = label.split("(")[-1].rstrip(")")
row = df[df["product_id"] == product_id].sort_values("date").iloc[-1]
prod_name = row["product_name"]
category_val = row.get("category", "General")

# Fetch time series & snapshot
series = get_daily_series(df, product_id)

with st.spinner(f"Compiling intelligence profile for {prod_name}..."):
    model_name, reason, _ = best_model_for_product(series, settings)
    fc = get_forecast(series, model_name, 30)

    rec = None
    if has_inv:
        snap_row = build_snapshot(df[df["product_id"] == product_id], settings).iloc[0]
        current_stock = snap_row["current_stock"]
        lead_time = snap_row["lead_time_days"]
        rec = build_recommendation(product_id, prod_name, series["demand"], fc, current_stock, lead_time, settings)

# -------------------------------------------------------------
# Product Header Banner
# -------------------------------------------------------------
health_status = rec.health if rec else "Active"
status_pill = render_status_badge(health_status)

st.markdown(
    f'<div class="fn-card" style="margin-bottom:1.25rem; padding:1.25rem 1.5rem;">'
    f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
    f'<div>'
    f'<div style="display:flex; align-items:center; gap:0.75rem;">'
    f'<h2 style="margin:0; font-size:1.6rem; font-weight:800; color:#F1F5F9;">{prod_name}</h2>'
    f'{status_pill}'
    f'</div>'
    f'<div style="margin-top:0.35rem; color:#8B9BB4; font-size:0.85rem;">'
    f'SKU: <b style="color:#F1F5F9;">{product_id}</b> &nbsp;·&nbsp; Category: <b style="color:#F1F5F9;">{category_val}</b> &nbsp;·&nbsp; Calibrated Model: <b style="color:#28B8FF;">{model_name}</b>'
    f'</div>'
    f'</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

# -------------------------------------------------------------
# KPI Row
# -------------------------------------------------------------
if has_inv and rec:
    c1, c2, c3 = st.columns(3)
    with c1:
        render_kpi_card("Current Stock", f"{rec.current_stock:,.0f} units", context="On-hand physical stock")
    with c2:
        render_kpi_card("30-Day Forward Demand", f"{fc['forecast'].sum():,.0f} units", context=f"Projected {model_name} volume")
    with c3:
        if rec.coverage_days < 0:
            if rec.current_stock <= 0:
                cov_str = "0 days"
                cov_status = "Critical"
                cov_ctx = "Depleted stock"
            else:
                cov_str = "∞ (Stagnant)"
                cov_status = "Watch"
                cov_ctx = "Zero recent velocity"
        else:
            cov_str = f"{rec.coverage_days:.0f} days"
            cov_status = "Critical" if rec.coverage_days <= 7 else ("Watch" if rec.coverage_days <= 14 else "Healthy")
            cov_ctx = f"Based on {rec.avg_daily_demand:.1f} units/day"
        render_kpi_card("Inventory Coverage", cov_str, status=cov_status, context=cov_ctx)

    st.write("")
    c4, c5, c6 = st.columns(3)
    with c4:
        render_kpi_card("Reorder Point (ROP)", f"{rec.reorder_point:,.0f} units", context=f"Lead time: {rec.lead_time_days:.0f} days")
    with c5:
        render_kpi_card("Safety Stock Buffer", f"{rec.safety_stock:,.0f} units", context=f"Target Service Level: {settings.service_level_z * 100:.0f}%")
    with c6:
        render_kpi_card(
            "Recommended Order",
            f"{rec.recommended_order_qty:,.0f} units",
            status="Critical" if rec.should_reorder else "Healthy",
            context="Immediate replenishment required" if rec.should_reorder else "Sufficient coverage — no order needed",
        )
else:
    c1, c2 = st.columns(2)
    with c1:
        render_kpi_card("30-Day Forecast", f"{fc['forecast'].sum():,.0f} units")
    with c2:
        render_kpi_card("Forecasting Engine", model_name, context=reason)

# -------------------------------------------------------------
# Visual Analytics
# -------------------------------------------------------------
render_section_header("Demand History & Forward Trajectory", f"Trailing 120 days demand velocity with 30-day forward projection ({model_name}).")
st.plotly_chart(create_demand_forecast_chart(series, fc, product_name=prod_name, history_tail_days=120), use_container_width=True)

if has_inv and rec:
    render_section_header("Inventory Depletion & Threshold Benchmark", "Historic stock on hand plotted against minimum safety reorder threshold.")
    inv_series = df[df["product_id"] == product_id].sort_values("date").tail(180)
    st.plotly_chart(create_current_stock_vs_forecast_chart(inv_series, rec.reorder_point, product_name=prod_name), use_container_width=True)

if "revenue" in df.columns:
    render_section_header("Revenue Generation", "Daily commercial value created by this SKU.")
    rev = df[df["product_id"] == product_id].sort_values("date").tail(180)
    st.plotly_chart(create_revenue_trend_chart(rev), use_container_width=True)

# -------------------------------------------------------------
# Decision Card
# -------------------------------------------------------------
if has_inv and rec:
    render_section_header("Replenishment Decision", "Automated inventory action recommendation.")
    render_recommendation_card(
        product_name=prod_name,
        risk_level=rec.stockout_risk,
        current_stock=rec.current_stock,
        expected_demand=rec.avg_daily_demand * rec.lead_time_days,
        safety_stock=rec.safety_stock,
        reorder_point=rec.reorder_point,
        recommended_order_qty=rec.recommended_order_qty,
        why_reason=rec.explanation,
    )
