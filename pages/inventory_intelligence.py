import streamlit as st
import pandas as pd
import numpy as np
from core.state import has_data
from ui.components import kpi_card, empty_state, section_title
from analytics.inventory import build_snapshot
from visualizations.inventory_charts import create_inventory_health_matrix, create_inventory_aging_chart

st.title("Inventory Intelligence")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to see inventory analytics.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns
has_price = "price" in df.columns

if not has_inv:
    empty_state("Inventory data unavailable", "This dataset has no inventory column, so inventory-level metrics cannot be calculated. Add an 'inventory' field in Data Lab to unlock this page.")
    st.stop()

# --- Same snapshot used by Command Center, Alerts, Recommendations ---
snap = build_snapshot(df, settings)
snap = snap.rename(columns={"current_stock": "stock"})
if has_price:
    snap["value"] = snap["stock"] * snap["price"]

total_units = int(snap["stock"].sum())
total_value = snap["value"].sum() if has_price and snap["value"].notna().any() else None
avg_coverage = snap.loc[snap["coverage_days"] >= 0, "coverage_days"].mean()
stockout_n = int((snap["health"] == "Critical").sum())

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Inventory Units", f"{total_units:,}")
with c2: kpi_card("Inventory Value", f"${total_value:,.0f}" if total_value is not None else "N/A — no price field")
with c3: kpi_card("Avg Coverage", f"{avg_coverage:.1f} days" if pd.notna(avg_coverage) else "N/A")
with c4: kpi_card("Critical Stockout Risk", f"{stockout_n} products")

section_title("Inventory Health Matrix", "Inventory level vs. demand level, classified by risk.")
st.plotly_chart(create_inventory_health_matrix(snap), use_container_width=True)

c1, c2 = st.columns(2)
with c1:
    section_title("Fast Movers", "Highest average daily demand.")
    st.dataframe(snap.sort_values("avg_daily_demand", ascending=False).head(10)[["product_name", "avg_daily_demand", "stock", "coverage_days"]],
                 use_container_width=True, hide_index=True)
with c2:
    section_title("Slow Movers", "Lowest demand relative to stock on hand.")
    slow = snap[snap["coverage_days"] >= 0].sort_values("coverage_days", ascending=False)
    st.dataframe(slow.head(10)[["product_name", "avg_daily_demand", "stock", "coverage_days"]],
                 use_container_width=True, hide_index=True)

section_title("Inventory Aging", "Estimated days of stock on hand, bucketed.")
bins = [0, 30, 60, 90, np.inf]
labels = ["0–30 days", "31–60 days", "61–90 days", "90+ days"]
aging_src = snap.copy()
aging_src["coverage_for_bucket"] = aging_src["coverage_days"].replace(-1, np.inf)
aging_src["age_bucket"] = pd.cut(aging_src["coverage_for_bucket"].fillna(0), bins=bins, labels=labels)
agg = aging_src.groupby("age_bucket", observed=True).agg(units=("stock", "sum")).reset_index()
st.plotly_chart(create_inventory_aging_chart(agg, value_col="units"), use_container_width=True)
