"""FORESIGHT Nexus — Inventory Intelligence Dashboard.

Analytical telemetry: inventory health matrix, ranked stockout risk, capital exposure,
coverage aging distribution (0-7, 8-14, 15-30, 30+ days), and SKU velocity tiers.
"""
import streamlit as st
import pandas as pd
import numpy as np
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_kpi_card, render_empty_state
from ui.tables import style_dataframe
from analytics.inventory import build_snapshot
from visualizations.inventory_charts import (
    create_inventory_health_matrix,
    create_inventory_aging_chart,
    create_stockout_risk_chart,
)

render_page_header(
    "Inventory Intelligence",
    "Physical stock distribution, stockout vulnerability, capital aging, and velocity segmentation.",
    meta_items=["Stockout Telemetry", "Aging Analysis", "Capital Exposure"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset Connected",
        "Upload your sales & inventory records in Data Lab or load the demo dataset to view inventory analytics.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns
has_price = "price" in df.columns

if not has_inv:
    render_empty_state(
        "Inventory Records Unavailable",
        "This dataset contains sales demand but no 'inventory' column. Upload a dataset with stock counts in Data Lab to unlock inventory intelligence.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

# Build snapshot
snap = build_snapshot(df, settings)
snap = snap.rename(columns={"current_stock": "stock"})
if has_price:
    snap["value"] = snap["stock"] * snap["price"]

total_units = int(snap["stock"].sum())
total_value = snap["value"].sum() if has_price and snap["value"].notna().any() else None
avg_coverage = snap.loc[snap["coverage_days"] >= 0, "coverage_days"].mean()
stockout_n = int((snap["health"] == "Critical").sum())
overstock_n = int((snap["health"] == "Watch").sum())

# -------------------------------------------------------------
# KPI Overview
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Stock on Hand", f"{total_units:,} units", context="Active physical units across SKUs")
with c2:
    val_str = f"${total_value:,.0f}" if total_value is not None else "N/A"
    render_kpi_card("Working Capital Valuation", val_str, context="Based on catalog unit prices" if total_value is not None else "No unit price field")
with c3:
    cov_str = f"{avg_coverage:.1f} days" if pd.notna(avg_coverage) else "N/A"
    render_kpi_card("Average Coverage Window", cov_str, context="Days of projected forward demand")
with c4:
    render_kpi_card(
        "Critical Stockout Urgency",
        f"{stockout_n} SKUs",
        status="Critical" if stockout_n > 0 else "Healthy",
        context=f"{overstock_n} SKUs overstocked",
    )

# -------------------------------------------------------------
# Health Matrix & Stockout Risk
# -------------------------------------------------------------
render_section_header("Inventory Health Matrix", "Two-dimensional mapping of Current Stock vs. Daily Demand velocity, classified by risk.")
st.plotly_chart(create_inventory_health_matrix(snap), use_container_width=True)

col_chart1, col_chart2 = st.columns([1, 1])
with col_chart1:
    render_section_header("Imminent Stockout Risk", "Products with shortest days of remaining stock before stockout.")
    st.plotly_chart(create_stockout_risk_chart(snap, top_n=10), use_container_width=True)

with col_chart2:
    render_section_header("Inventory Coverage Aging", "Distribution of catalog stock volume across forward coverage windows.")
    # Meaningful enterprise buckets: 0–7 days, 8–14 days, 15–30 days, 30+ days
    bins = [0, 7, 14, 30, np.inf]
    bucket_labels = ["0–7 days (Critical)", "8–14 days (Watch)", "15–30 days (Healthy)", "30+ days (Overstock)"]
    aging_src = snap.copy()
    aging_src["coverage_for_bucket"] = aging_src["coverage_days"].replace(-1, np.inf)
    aging_src["age_bucket"] = pd.cut(aging_src["coverage_for_bucket"].fillna(0), bins=bins, labels=bucket_labels)
    agg = aging_src.groupby("age_bucket", observed=True).agg(units=("stock", "sum")).reset_index()
    st.plotly_chart(create_inventory_aging_chart(agg, value_col="units"), use_container_width=True)

# -------------------------------------------------------------
# Velocity Segmentation: Fast vs. Slow Movers
# -------------------------------------------------------------
render_section_header("Demand Velocity Segmentation", "Fast movers vs. slow-moving stock requiring demand stimulation.")
col_tab1, col_tab2 = st.columns(2)

with col_tab1:
    st.write("**Top Velocity Items (Fast Movers):**")
    fast = snap.sort_values("avg_daily_demand", ascending=False).head(10)[["product_name", "avg_daily_demand", "stock", "coverage_days"]]
    fast.columns = ["Product", "Avg Daily Demand", "Stock", "Coverage (Days)"]
    style_dataframe(fast)

with col_tab2:
    st.write("**Excess Coverage Lines (Slow Movers):**")
    slow = snap[snap["coverage_days"] >= 0].sort_values("coverage_days", ascending=False).head(10)[["product_name", "avg_daily_demand", "stock", "coverage_days"]]
    slow.columns = ["Product", "Avg Daily Demand", "Stock", "Coverage (Days)"]
    style_dataframe(slow)
