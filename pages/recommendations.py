"""FORESIGHT Nexus — Replenishment Recommendations.

Decision-oriented interface: prioritizes replenishment orders by urgency (Critical, High, Watch),
clearly displaying recommended purchase quantities, key formula inputs, and business rationales.
"""
import streamlit as st
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_empty_state, render_recommendation_card, render_kpi_card
from analytics.inventory import build_snapshot
from recommendations.engine import build_recommendation
from utils.pipeline import get_daily_series
from visualizations.recommendation_charts import create_reorder_recommendation_chart
import pandas as pd

render_page_header(
    "Replenishment Recommendations",
    "Automated purchase order proposals calibrated against forecast velocity and supplier lead times.",
    meta_items=["95% Service Level Target", "Lead-Time Sizing", "Safety Stock Protection"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset Connected",
        "Upload your sales & inventory history in Data Lab or load the demo dataset to review reorder recommendations.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

if not has_inv:
    render_empty_state(
        "Inventory Records Unavailable",
        "Reorder proposals require stock levels. Upload a dataset with an 'inventory' column in Data Lab to activate recommendations.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

# Build snapshot
snap = build_snapshot(df, settings)
eligible = snap[snap["should_reorder"]]

recs = []
for pid in eligible["product_id"]:
    g = df[df["product_id"] == pid].sort_values("date")
    series = get_daily_series(df, pid)
    stock = g["inventory"].iloc[-1]
    lead_time = eligible.loc[eligible["product_id"] == pid, "lead_time_days"].iloc[0]
    rec = build_recommendation(pid, g["product_name"].iloc[0], series["demand"], None, stock, lead_time, settings)
    recs.append(rec)

# Sort: most urgent first (lowest coverage)
recs.sort(key=lambda r: r.coverage_days if r.coverage_days >= 0 else 9999)

n_critical = sum(1 for r in recs if r.stockout_risk == "Critical")
n_high = sum(1 for r in recs if r.stockout_risk == "High")
n_watch = sum(1 for r in recs if r.stockout_risk in ("Medium", "Watch", "Low"))
total_units_rec = sum(r.recommended_order_qty for r in recs)

# Summary KPI row
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Total Orders Required", f"{len(recs)} SKUs", context="Items breaching reorder thresholds")
with c2:
    render_kpi_card("Critical Urgency", f"{n_critical} SKUs", status="Critical" if n_critical > 0 else "Healthy", context="Stockout projected within 7 days")
with c3:
    render_kpi_card("High Priority", f"{n_high} SKUs", status="High" if n_high > 0 else "Healthy", context="Stockout projected within lead time")
with c4:
    render_kpi_card("Recommended Volume", f"{total_units_rec:,.0f} units", context="Total order quantity across catalog")

# Action bar & filter
render_section_header(f"{len(recs)} ACTIONS REQUIRE IMMEDIATE DECISION")

if not recs:
    st.success("✅ All catalog SKUs are currently operating within safe inventory thresholds. No replenishment orders needed.")
else:
    # Top Replenishment Chart
    rec_df = pd.DataFrame([{
        "product_name": r.product_name,
        "recommended_order_qty": r.recommended_order_qty,
        "risk": r.stockout_risk,
    } for r in recs])
    st.plotly_chart(create_reorder_recommendation_chart(rec_df, top_n=8), use_container_width=True)

    filter_tab_all, filter_tab_crit, filter_tab_high, filter_tab_watch = st.tabs([
        f"All Actions ({len(recs)})",
        f"Critical ({n_critical})",
        f"High ({n_high})",
        f"Watch ({n_watch})",
    ])

    def render_rec_list(items):
        if not items:
            st.info("No items in this urgency tier.")
            return
        for r in items:
            render_recommendation_card(
                product_name=r.product_name,
                risk_level=r.stockout_risk,
                current_stock=r.current_stock,
                expected_demand=r.avg_daily_demand * r.lead_time_days,
                safety_stock=r.safety_stock,
                reorder_point=r.reorder_point,
                recommended_order_qty=r.recommended_order_qty,
                why_reason=r.explanation,
            )

    with filter_tab_all:
        render_rec_list(recs)
    with filter_tab_crit:
        render_rec_list([r for r in recs if r.stockout_risk == "Critical"])
    with filter_tab_high:
        render_rec_list([r for r in recs if r.stockout_risk == "High"])
    with filter_tab_watch:
        render_rec_list([r for r in recs if r.stockout_risk not in ("Critical", "High")])
