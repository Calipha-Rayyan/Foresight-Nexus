"""FORESIGHT Nexus — Demand Intelligence.

Holistic sales velocity, macro demand trajectories, multi-scale seasonality patterns,
and SKU-level growth and contraction segmentation.
"""
import streamlit as st
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_kpi_card, render_empty_state
from ui.tables import style_dataframe
from analytics.demand import demand_growth_pct, volatility, category_demand, top_growth_products
from visualizations.demand_charts import (
    create_demand_trend_chart,
    create_weekly_seasonality_chart,
    create_monthly_seasonality_chart,
    create_category_demand_chart,
)

render_page_header(
    "Demand Intelligence",
    "Analyze baseline sales velocity, identify cyclical patterns, and monitor emerging product growth leaders.",
    meta_items=["Macro Demand Trajectory", "Multi-Cycle Seasonality", "Velocity Segmentation"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset Connected",
        "Upload your sales history in Data Lab or load the demo dataset to unlock demand intelligence.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
daily = df.groupby("date", as_index=False)["quantity"].sum().rename(columns={"quantity": "demand"})
daily = daily.set_index("date").asfreq("D", fill_value=0).reset_index()

total_demand = int(df["quantity"].sum())
growth = demand_growth_pct(daily)
avg_daily = round(daily["demand"].tail(90).mean(), 1)
vol = volatility(daily)

# -------------------------------------------------------------
# Demand Overview KPIs
# -------------------------------------------------------------
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Cumulative Demand", f"{total_demand:,} units", context="Across all catalog SKUs")
with c2:
    growth_str = f"{growth:+.1f}%" if growth is not None else None
    render_kpi_card(
        "Demand Growth (28d)",
        growth_str or "Stable",
        delta=growth_str,
        delta_positive=(growth or 0) >= 0,
        context="vs. trailing 28-day baseline",
    )
with c3:
    render_kpi_card("Average Daily Velocity", f"{avg_daily:,.1f} units", context="Rolling 90-day mean daily volume")
with c4:
    vol_status = "Healthy" if vol < 20 else ("Watch" if vol < 40 else "High")
    render_kpi_card("Demand Volatility (CV)", f"{vol:.1f}%", status=vol_status, context="Coefficient of variation, last 28 days")

# -------------------------------------------------------------
# Macro Demand Trajectory
# -------------------------------------------------------------
render_section_header("Aggregate Demand Velocity", "Daily observed sales volume plotted across the historical timeline.")
st.plotly_chart(create_demand_trend_chart(daily), use_container_width=True)

# -------------------------------------------------------------
# Seasonality Patterns
# -------------------------------------------------------------
render_section_header("Cyclical Demand Patterns", "Day-of-week and month-of-year seasonal demand fluctuations.")
col_s1, col_s2 = st.columns(2)
with col_s1:
    st.plotly_chart(create_weekly_seasonality_chart(df), use_container_width=True)
with col_s2:
    st.plotly_chart(create_monthly_seasonality_chart(df), use_container_width=True)

# -------------------------------------------------------------
# Category Breakdown & SKU Movers
# -------------------------------------------------------------
if "category" in df.columns:
    render_section_header("Category Distribution", "Total volume demanded across catalog categories.")
    cat = category_demand(df)
    st.plotly_chart(create_category_demand_chart(cat), use_container_width=True)

render_section_header("Velocity Leaders & Contractions", "Emerging sales drivers vs. slowing product lines requiring marketing review.")
col_m1, col_m2 = st.columns(2)
with col_m1:
    st.write("**Strongest Demand Acceleration (28-day vs. Prior 28-day):**")
    growers = top_growth_products(df, top_n=8)
    if len(growers):
        style_dataframe(growers)
    else:
        st.caption("Insufficient historical timeline to compute growth acceleration (requires 56+ days).")

with col_m2:
    st.write("**Steepest Demand Contraction:**")
    decliners = top_growth_products(df, top_n=200).sort_values("growth_pct").head(8)
    if len(decliners):
        style_dataframe(decliners)
    else:
        st.caption("Insufficient historical timeline to compute demand contraction (requires 56+ days).")
