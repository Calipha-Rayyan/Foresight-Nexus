"""FORESIGHT Nexus — Alerts & Risk Center.

Intelligent threat detection: identifies stockout risks before supplier lead times elapse,
highlights excess inventory capital lockup, and isolates statistical demand anomalies.
"""
import streamlit as st
import pandas as pd
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_empty_state, render_alert_card, render_kpi_card
from ui.tables import style_dataframe
from analytics.inventory import build_snapshot
from analytics.risk import demand_trend_flag
from analytics.anomalies import detect_anomalies
from utils.pipeline import get_daily_series

render_page_header(
    "Alerts & Risk Center",
    "Continuous risk monitoring across inventory depletion, overstock capital lockup, and demand volatility.",
    meta_items=["Real-time Anomaly Detection", "Stockout Horizon Alerts", "Lead-Time Buffering"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset Connected",
        "Upload sales records in Data Lab or activate demo mode to scan for inventory and demand risks.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns

alerts = []

# 1. Inventory Alerts (Stockout & Overstock)
if has_inv:
    snap = build_snapshot(df, settings)
    for _, row in snap.iterrows():
        p_name = row["product_name"]
        cat = row.get("category", "General")
        lead_time = row["lead_time_days"]
        cov = row["coverage_days"]

        if row["stockout_risk"] in ("Critical", "High"):
            dts = row["days_to_stockout"]
            body = (
                f"Projected stockout in {dts:.0f} days (Supplier lead time is {lead_time:.0f} days). "
                f"Immediate reorder necessary to avoid fulfillment interruption."
                if dts >= 0 else "Demand velocity is outpacing available inventory on hand."
            )
            impact = f"Potential loss of {row['avg_daily_demand']:.0f} daily units in customer sales."
            action = f"Issue purchase order to satisfy lead time ({lead_time:.0f} days) + safety buffer."
            alerts.append({
                "severity": row["stockout_risk"],
                "category": cat,
                "title": f"{p_name} — Imminent Stockout Risk",
                "body": body,
                "impact": impact,
                "action": action,
            })
        elif row["overstock_risk"] in ("Critical", "High"):
            body = (
                f"Inventory on hand provides {cov:.0f} days of demand coverage, "
                f"significantly exceeding the {settings.overstock_days_threshold}-day policy threshold."
            )
            impact = "Working capital is trapped in slow-moving inventory with potential depreciation risk."
            action = "Pause pending replenishment; evaluate promotional demand stimulation."
            alerts.append({
                "severity": "Medium",
                "category": cat,
                "title": f"{p_name} — Overstock Capital Lockup",
                "body": body,
                "impact": impact,
                "action": action,
            })

# 2. Demand Velocity Shift Alerts
for pid, g in df.groupby("product_id"):
    g = g.sort_values("date")
    name = g["product_name"].iloc[0]
    cat = g["category"].iloc[0] if "category" in g.columns else "General"
    if len(g) < 56:
        continue
    avg_d = g["quantity"].tail(28).mean()
    prior_avg = g["quantity"].tail(56).head(28).mean()
    trend = demand_trend_flag(avg_d, prior_avg)
    if trend:
        pct_change = ((avg_d - prior_avg) / prior_avg * 100) if prior_avg > 0 else 0
        severity = "High" if abs(pct_change) > 40 else "Medium"
        impact = f"Baseline sales velocity shifted by {pct_change:+.1f}%, altering inventory run-rate."
        action = "Recalibrate SKU forecast parameters in Forecast Studio and adjust supplier schedules."
        alerts.append({
            "severity": severity,
            "category": cat,
            "title": f"{name} — {trend}",
            "body": f"28-day demand shifted from {prior_avg:.1f} to {avg_d:.1f} units/day ({pct_change:+.1f}%).",
            "impact": impact,
            "action": action,
        })

# Sort alerts by severity
sev_rank = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
alerts.sort(key=lambda a: sev_rank.get(a["severity"], 4))

n_crit = sum(1 for a in alerts if a["severity"] == "Critical")
n_high = sum(1 for a in alerts if a["severity"] == "High")
n_med = sum(1 for a in alerts if a["severity"] == "Medium")
n_low = sum(1 for a in alerts if a["severity"] == "Low")

# KPI Summary Row
c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Critical Alerts", f"{n_crit}", status="Critical" if n_crit > 0 else "Healthy", context="Requires same-day response")
with c2:
    render_kpi_card("High Priority", f"{n_high}", status="High" if n_high > 0 else "Healthy", context="Requires action this week")
with c3:
    render_kpi_card("Watchlist Items", f"{n_med}", status="Watch" if n_med > 0 else "Healthy", context="Velocity & overstock shifts")
with c4:
    render_kpi_card("Total Flagged Items", f"{len(alerts)}", context="Across all monitored categories")

# -------------------------------------------------------------
# Filters
# -------------------------------------------------------------
render_section_header("Active Risk Items", "Filter by urgency tier or catalog category.")
col_f1, col_f2 = st.columns([1, 1])
with col_f1:
    filter_sev = st.selectbox("Filter Urgency Tier", ["All Severities", "Critical", "High", "Medium"])
with col_f2:
    cats = ["All Categories"] + sorted(list(set(a["category"] for a in alerts)))
    filter_cat = st.selectbox("Filter Category", cats)

filtered_alerts = alerts
if filter_sev != "All Severities":
    filtered_alerts = [a for a in filtered_alerts if a["severity"] == filter_sev]
if filter_cat != "All Categories":
    filtered_alerts = [a for a in filtered_alerts if a["category"] == filter_cat]

if not filtered_alerts:
    st.success("✅ No alerts match the selected criteria.")
else:
    for a in filtered_alerts[:30]:
        render_alert_card(
            title=a["title"],
            body=a["body"],
            action=a["action"],
            severity=a["severity"].lower(),
            category=a["category"],
            impact=a["impact"],
        )

# -------------------------------------------------------------
# Anomaly Detection Table
# -------------------------------------------------------------
render_section_header("Statistical Anomaly Detection", "Unusual single-day demand spikes or collapses (z-score ≥ 2.5 vs. 14-day rolling baseline).")
sample_products = df["product_id"].unique()[:20]
anomaly_rows = []
for pid in sample_products:
    series = get_daily_series(df, pid)
    anoms = detect_anomalies(series)
    if len(anoms):
        name = df[df["product_id"] == pid]["product_name"].iloc[0]
        cat = df[df["product_id"] == pid]["category"].iloc[0] if "category" in df.columns else "General"
        for _, row in anoms.tail(2).iterrows():
            anomaly_rows.append({
                "Product": name,
                "Category": cat,
                "Date": str(row["date"].date()),
                "Observed Demand": f"{int(row['demand']):,} units",
                "Z-Score": f"{row['z_score']:.2f}",
                "Finding": row["anomaly_type"],
            })

if anomaly_rows:
    style_dataframe(pd.DataFrame(anomaly_rows))
else:
    st.caption("No statistical anomalies detected in current active sampling window.")
