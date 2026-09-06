import streamlit as st
from core.state import has_data
from ui.components import empty_state, section_title, render_pill
from analytics.inventory import build_snapshot
from recommendations.engine import build_recommendation
from utils.pipeline import get_daily_series

st.title("Recommendations")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to see recommendations.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

if not has_inv:
    empty_state("Inventory data unavailable", "Reorder recommendations require an inventory field. Add one in Data Lab to unlock this page.")
    st.stop()

# Same snapshot as Command Center / Alerts — the products flagged here are
# guaranteed to match the "products recommended for reorder" count shown elsewhere.
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

recs.sort(key=lambda r: r.coverage_days if r.coverage_days >= 0 else 9999)

section_title(f"{len(recs)} Products Recommended for Reorder")
if not recs:
    st.success("No products currently require reordering.")
for r in recs[:50]:
    with st.container(border=True):
        c1, c2 = st.columns([3, 1])
        with c1:
            st.markdown(f"**{r.product_name}**  {render_pill(r.stockout_risk)}", unsafe_allow_html=True)
            st.caption(r.explanation)
        with c2:
            st.metric("Order Qty", f"{r.recommended_order_qty:.0f}")
