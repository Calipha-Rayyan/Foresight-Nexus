import streamlit as st
import pandas as pd
from core.state import has_data
from core.constants import HEALTH_CRITICAL, HEALTH_AT_RISK, HEALTH_WATCH
from ui.components import render_hero, kpi_card, empty_state, section_title
from analytics.inventory import build_snapshot
from visualizations.forecast_charts import create_demand_forecast_chart
from forecasting.predictor import forecast as run_forecast

st.title("")  # hero replaces title

if not has_data():
    render_hero("Intelligence Engine Idle", "—", "No model loaded")
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset in Data Lab to activate FORESIGHT Nexus intelligence.")
    if st.button("Go to Data Lab", type="primary"):
        st.switch_page("pages/data_lab.py")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]

render_hero("Intelligence Engine Active", str(df["date"].max().date()), "Ready")

total_products = df["product_id"].nunique()
has_inv = "inventory" in df.columns
total_inventory = int(df.sort_values("date").groupby("product_id")["inventory"].last().sum()) if has_inv else None

recent_cut = df["date"].max() - pd.Timedelta(days=28)
prior_cut = recent_cut - pd.Timedelta(days=28)
recent_demand = df[df["date"] > recent_cut]["quantity"].sum()
prior_demand = df[(df["date"] > prior_cut) & (df["date"] <= recent_cut)]["quantity"].sum()
demand_growth = ((recent_demand - prior_demand) / prior_demand * 100) if prior_demand > 0 else None

# --- Single source of truth for every product's risk/stock state ---
snap = build_snapshot(df, settings) if has_inv else pd.DataFrame()

low_stock = int((snap["health"].isin([HEALTH_CRITICAL, HEALTH_AT_RISK])).sum()) if len(snap) else 0
overstock = int((snap["health"] == HEALTH_WATCH).sum()) if len(snap) else 0
reorder_count = int(snap["should_reorder"].sum()) if len(snap) else 0

reorder_value = None
if len(snap) and snap["price"].notna().any():
    at_risk = snap[snap["should_reorder"]]
    reorder_value = float((at_risk["avg_daily_demand"] * at_risk["lead_time_days"] * at_risk["price"].fillna(0)).sum())

c1, c2, c3, c4 = st.columns(4)
with c1: kpi_card("Total Products", f"{total_products}")
with c2: kpi_card("Inventory Units", f"{total_inventory:,}" if total_inventory is not None else "N/A — no inventory field")
with c3: kpi_card("28-Day Demand", f"{int(recent_demand):,}",
                   delta=f"{demand_growth:.1f}%" if demand_growth is not None else None,
                   delta_positive=(demand_growth or 0) >= 0)
with c4: kpi_card("Low Stock Products", f"{low_stock}", context=f"{overstock} overstocked")

c5, c6 = st.columns(2)
with c5:
    kpi_card("Recommended Reorder Value", f"${reorder_value:,.0f}" if reorder_value is not None else "N/A — no price field",
              context="Estimated cost to cover lead-time demand for at-risk products")
with c6:
    kpi_card("Overstock Risk", f"{overstock} products", context=f"≥{settings.overstock_days_threshold} days of coverage")

# --- Executive summary (dynamically generated from the same snapshot) ---
section_title("Executive Summary")
top_cat = None
if len(snap) and "category" in snap.columns:
    cat_risk = snap[snap["health"].isin([HEALTH_CRITICAL, HEALTH_AT_RISK])]["category"].value_counts()
    top_cat = cat_risk.idxmax() if len(cat_risk) else None

trend_word = "trending upward" if (demand_growth or 0) >= 0 else "trending downward"
summary_lines = [
    f"Overall demand is **{trend_word}** ({demand_growth:+.1f}% over the last 28 days)." if demand_growth is not None else "Not enough history yet to establish a demand trend.",
    f"**{low_stock} product(s)** require immediate attention due to low inventory coverage." if has_inv else "Inventory coverage cannot be assessed — no inventory field in this dataset.",
    f"Inventory risk is concentrated in the **{top_cat}** category." if top_cat else "No concentrated category risk detected.",
    f"**{reorder_count} product(s)** are recommended for reorder based on current stock vs. lead-time demand." if has_inv else "Reorder recommendations require an inventory field.",
]
for line in summary_lines:
    st.markdown(f"- {line}")

# --- Hero forecast chart ---
section_title("Demand Outlook", "Historical total demand and a near-term aggregate forecast.")
daily_total = df.groupby("date", as_index=False)["quantity"].sum().rename(columns={"quantity": "demand"})
daily_total = daily_total.set_index("date").asfreq("D", fill_value=0).reset_index()

agg_model = "Moving Average" if len(daily_total) < settings.min_history_days_for_ml else "Linear Regression"
fc = run_forecast(daily_total, agg_model, settings.forecast_horizon_days)

fig = create_demand_forecast_chart(daily_total, fc, history_tail_days=120)
st.plotly_chart(fig, use_container_width=True)
st.caption(f"Aggregate forecast generated with {agg_model}. Product-level forecasts with model selection are available in Forecast Studio.")
