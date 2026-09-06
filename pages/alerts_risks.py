import streamlit as st
import pandas as pd
from core.state import has_data
from ui.components import empty_state, section_title, alert_card
from analytics.inventory import build_snapshot
from analytics.risk import demand_trend_flag
from analytics.anomalies import detect_anomalies
from utils.pipeline import get_daily_series

st.title("Alerts & Risks")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to see alerts.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

alerts = []

if has_inv:
    # Same snapshot used by Command Center / Inventory Intelligence / Recommendations —
    # guarantees this page agrees with the rest of the app on every product's risk state.
    snap = build_snapshot(df, settings)
    for _, row in snap.iterrows():
        if row["stockout_risk"] in ("Critical", "High"):
            dts_text = f"Projected stockout in {row['days_to_stockout']:.0f} days." if row["days_to_stockout"] >= 0 else "No recent demand to project stockout."
            alerts.append({"severity": row["stockout_risk"], "title": row["product_name"], "body": dts_text,
                            "action": f"Reorder to cover lead time ({row['lead_time_days']:.0f} days) plus safety stock."})
        elif row["overstock_risk"] in ("Critical", "High"):
            alerts.append({"severity": row["overstock_risk"], "title": row["product_name"],
                            "body": f"Inventory covers {row['coverage_days']:.0f} days of demand — well above the {settings.overstock_days_threshold}-day overstock threshold.",
                            "action": "Consider a promotion or pausing replenishment."})
else:
    st.info("No inventory column found — stockout/overstock alerts require an inventory field. Demand-trend alerts are still shown below.")

for pid, g in df.groupby("product_id"):
    g = g.sort_values("date")
    name = g["product_name"].iloc[0]
    if len(g) < 56:
        continue
    avg_d = g["quantity"].tail(28).mean()
    prior_avg = g["quantity"].tail(56).head(28).mean()
    trend = demand_trend_flag(avg_d, prior_avg)
    if trend:
        alerts.append({"severity": "Medium", "title": f"{name} — {trend}",
                        "body": f"28-day average demand moved from {prior_avg:.1f} to {avg_d:.1f} units/day.",
                        "action": "Review forecast in Forecast Studio and adjust reorder plan."})

sev_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
alerts.sort(key=lambda a: sev_order.get(a["severity"], 4))

c1, c2, c3 = st.columns(3)
with c1: st.metric("Critical", sum(1 for a in alerts if a["severity"] == "Critical"))
with c2: st.metric("High", sum(1 for a in alerts if a["severity"] == "High"))
with c3: st.metric("Medium", sum(1 for a in alerts if a["severity"] == "Medium"))

section_title("Active Alerts")
if not alerts:
    st.success("No active alerts. All monitored products are within healthy thresholds.")
else:
    for a in alerts[:40]:
        alert_card(a["title"], a["body"], a["action"], severity=a["severity"])

section_title("Anomaly Detection", "Statistically unusual demand spikes or drops (z-score ≥ 2.5 vs 14-day rolling baseline).")
sample_products = df["product_id"].unique()[:15]
anomaly_rows = []
for pid in sample_products:
    series = get_daily_series(df, pid)
    anomalies = detect_anomalies(series)
    if len(anomalies):
        name = df[df["product_id"] == pid]["product_name"].iloc[0]
        for _, row in anomalies.tail(3).iterrows():
            anomaly_rows.append({"product": name, "date": row["date"].date(), "demand": int(row["demand"]),
                                  "z_score": round(row["z_score"], 2), "finding": row["anomaly_type"]})
if anomaly_rows:
    st.dataframe(pd.DataFrame(anomaly_rows), use_container_width=True, hide_index=True)
else:
    st.caption("No statistically significant anomalies detected in the sampled products.")
