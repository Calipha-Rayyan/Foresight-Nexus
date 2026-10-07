"""FORESIGHT Nexus — Command Center.

Visual Narrative:
1. OVERVIEW (Current catalog, demand velocity, inventory volume, and risk count)
2. DEMAND OUTLOOK (Hero aggregate forecast with confidence interval)
3. INVENTORY RISK (Imminent stockouts and portfolio risk distribution)
4. PRIORITY ACTIONS (Executive insights and top actionable replenishment decisions)
"""
import streamlit as st
import pandas as pd
from core.state import has_data
from core.constants import HEALTH_CRITICAL, HEALTH_AT_RISK, HEALTH_WATCH
from ui.cards import render_hero, render_kpi_card, render_empty_state, render_recommendation_card
from ui.headers import render_section_header
from ui.insights import render_insight_card
from analytics.inventory import build_snapshot
from visualizations.forecast_charts import create_demand_forecast_chart
from visualizations.inventory_charts import create_stockout_risk_chart
from visualizations.risk_charts import create_risk_distribution_chart
from forecasting.predictor import forecast as run_forecast
from recommendations.engine import build_recommendation
from utils.pipeline import get_daily_series
from data.sample.generate_sample import generate_sample_dataset
from core.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS
from database.repositories import SalesRepository
from data.loader import load_file, apply_mapping, clean_dataset, guess_column
from utils.logging import log_error

if not has_data():
    render_hero("Intelligence Engine Standing By", "—", "Awaiting Data Ingestion", show_visual=False)
    render_section_header(
        "Connect Enterprise Dataset",
        "Upload your organization's historical sales, order logs, or inventory records to activate real-time demand sensing and inventory intelligence."
    )

    c1, c2 = st.columns([1.4, 1.6])
    with c1:
        st.markdown(
            '<div class="fn-card" style="padding:1.4rem 1.6rem; height:100%; display:flex; flex-direction:column; justify-content:space-between;">'
            '<div>'
            '<div style="font-size:1.15rem; font-weight:700; color:#F1F5F9; margin-bottom:0.4rem;">📁 Ingest Real-World Dataset</div>'
            '<p style="font-size:0.86rem; color:#8B9BB4; line-height:1.5; margin-bottom:1rem;">'
            'Connect your enterprise sales, inventory, or orders records. Our automated data hygiene pipeline cleans currency signs, normalizes mixed date formats, deduplicates transactions, and maps custom column schemas.'
            '</p>'
            '</div>'
            '</div>',
            unsafe_allow_html=True
        )
        if st.button("🚀 Launch Data Lab & Schema Alignment", type="primary", use_container_width=True):
            st.switch_page("pages/data_lab.py")

    with c2:
        st.markdown(
            '<div class="fn-card" style="padding:1.4rem 1.6rem; height:100%;">'
            '<div style="font-size:1.15rem; font-weight:700; color:#F1F5F9; margin-bottom:0.4rem;">⚡ Quick Ingestion Dropzone</div>'
            '<p style="font-size:0.86rem; color:#8B9BB4; line-height:1.5; margin-bottom:0.75rem;">'
            'Drop your CSV or Excel file here to analyze immediately:'
            '</p>'
            '</div>',
            unsafe_allow_html=True
        )
        quick_file = st.file_uploader(
            "Upload CSV or XLSX",
            type=["csv", "xlsx", "xls"],
            key="cc_quick_file",
            label_visibility="collapsed"
        )
        if quick_file is not None:
            try:
                raw_df = load_file(quick_file)
                auto_map = {}
                for req in REQUIRED_COLUMNS:
                    guessed = guess_column(req, list(raw_df.columns))
                    if guessed:
                        auto_map[req] = guessed
                for opt in OPTIONAL_COLUMNS:
                    guessed = guess_column(opt, list(raw_df.columns))
                    if guessed:
                        auto_map[opt] = guessed

                missing_req = [r for r in REQUIRED_COLUMNS if r not in auto_map]
                if not missing_req:
                    with st.spinner("Analyzing and ingesting enterprise records..."):
                        mapped = apply_mapping(raw_df, auto_map)
                        cleaned, log = clean_dataset(mapped)
                        st.session_state["dataset"] = cleaned
                        st.session_state["demo_mode"] = False
                        st.session_state["cleaning_log"] = log
                        st.session_state["column_mapping"] = auto_map
                        try:
                            SalesRepository.load(cleaned)
                        except Exception as e:
                            log_error("DuckDB load error on quick ingestion", e)
                        st.success(f"✅ Real-world dataset ingested: {len(cleaned):,} records across {cleaned['product_id'].nunique()} SKUs.")
                        st.rerun()
                else:
                    st.info(f"Custom mapping needed for: {', '.join(missing_req)}. Opening Data Lab...")
                    st.session_state["pending_file"] = quick_file
                    st.switch_page("pages/data_lab.py")
            except Exception as e:
                log_error("Quick file parse error", e)
                st.error(f"Error parsing file: {e}")

    st.write("")
    with st.expander("🧪 Sandbox Evaluation Mode: Load Synthetic Demo Dataset"):
        st.caption(
            "Evaluating FORESIGHT Nexus? You can explore the full platform capabilities using a pre-calibrated "
            "synthetic dataset with multi-seasonal demand, promotions, and inventory depletion cycles."
        )
        if st.button("Activate Evaluation Sandbox", type="secondary"):
            with st.spinner("Initializing synthetic market environment..."):
                df = generate_sample_dataset()
            st.session_state["dataset"] = df
            st.session_state["demo_mode"] = True
            st.session_state["cleaning_log"] = ["Demo dataset activated — verified clean."]
            st.session_state["column_mapping"] = {c: c for c in REQUIRED_COLUMNS + OPTIONAL_COLUMNS if c in df.columns}
            try:
                SalesRepository.load(df)
            except Exception:
                pass
            st.rerun()

    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]
has_inv = "inventory" in df.columns
has_price = "price" in df.columns

# Calculate core metrics
total_products = df["product_id"].nunique()
total_inventory = int(df.sort_values("date").groupby("product_id")["inventory"].last().sum()) if has_inv else None

recent_cut = df["date"].max() - pd.Timedelta(days=28)
prior_cut = recent_cut - pd.Timedelta(days=28)
recent_demand = df[df["date"] > recent_cut]["quantity"].sum()
prior_demand = df[(df["date"] > prior_cut) & (df["date"] <= recent_cut)]["quantity"].sum()
demand_growth = ((recent_demand - prior_demand) / prior_demand * 100) if prior_demand > 0 else None

# Inventory snapshot single source of truth
snap = build_snapshot(df, settings) if has_inv else pd.DataFrame()
low_stock = int((snap["health"].isin([HEALTH_CRITICAL, HEALTH_AT_RISK])).sum()) if len(snap) else 0
overstock = int((snap["health"] == HEALTH_WATCH).sum()) if len(snap) else 0
reorder_count = int(snap["should_reorder"].sum()) if len(snap) else 0

reorder_value = None
if len(snap) and snap["price"].notna().any():
    at_risk = snap[snap["should_reorder"]]
    reorder_value = float((at_risk["avg_daily_demand"] * at_risk["lead_time_days"] * at_risk["price"].fillna(0)).sum())

# Hero Header with Data Nexus
last_date = str(df["date"].max().date())
render_hero("Intelligence Engine Active", last_date, "Calibrated & Serving", show_visual=True)

# -------------------------------------------------------------
# 1. OVERVIEW
# -------------------------------------------------------------
render_section_header("Overview", "High-level demand velocity and inventory status.")

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Catalog Monitored", f"{total_products}", context="Active product lines")
with c2:
    render_kpi_card(
        "Inventory on Hand",
        f"{total_inventory:,} units" if total_inventory is not None else "N/A",
        context="Aggregate physical stock" if total_inventory is not None else "No inventory field",
    )
with c3:
    growth_str = f"{demand_growth:+.1f}%" if demand_growth is not None else None
    render_kpi_card(
        "28-Day Demand Velocity",
        f"{int(recent_demand):,} units",
        delta=growth_str,
        delta_positive=(demand_growth or 0) >= 0,
        context="vs. prior 28-day baseline",
    )
with c4:
    render_kpi_card(
        "Stockout Exposure",
        f"{low_stock} products",
        status="Critical" if low_stock > 5 else ("Watch" if low_stock > 0 else "Healthy"),
        context=f"{overstock} overstocked lines",
    )

c5, c6 = st.columns(2)
with c5:
    render_kpi_card(
        "Recommended Purchase Orders",
        f"${reorder_value:,.0f}" if reorder_value is not None else f"{reorder_count} products pending",
        status="High" if reorder_count > 0 else "Healthy",
        context=f"Estimated capital required to satisfy lead times for {reorder_count} critical items",
    )
with c6:
    render_kpi_card(
        "Overstock Working Capital",
        f"{overstock} products",
        status="Watch" if overstock > 0 else "Healthy",
        context=f"Exceeds {settings.overstock_days_threshold} days of projected forward coverage",
    )

# -------------------------------------------------------------
# 2. DEMAND OUTLOOK
# -------------------------------------------------------------
render_section_header("Demand Outlook", "Historical total demand trend and automated 30-day forecast.")

daily_total = df.groupby("date", as_index=False)["quantity"].sum().rename(columns={"quantity": "demand"})
daily_total = daily_total.set_index("date").asfreq("D", fill_value=0).reset_index()

agg_model = "Moving Average" if len(daily_total) < settings.min_history_days_for_ml else "Linear Regression"
fc = run_forecast(daily_total, agg_model, settings.forecast_horizon_days)

fig_outlook = create_demand_forecast_chart(
    daily_total,
    fc,
    product_name="Catalog Aggregate",
    history_tail_days=120,
    title=f"Total Catalog Demand — {settings.forecast_horizon_days}-Day Outlook ({agg_model})",
)
st.plotly_chart(fig_outlook, use_container_width=True)

# -------------------------------------------------------------
# 3. INVENTORY RISK
# -------------------------------------------------------------
if has_inv and len(snap):
    render_section_header("Inventory Risk", "Stockout vulnerability and portfolio health breakdown.")
    col_r1, col_r2 = st.columns([3, 2])
    with col_r1:
        st.plotly_chart(create_stockout_risk_chart(snap, top_n=8), use_container_width=True)
    with col_r2:
        st.plotly_chart(create_risk_distribution_chart(snap), use_container_width=True)

# -------------------------------------------------------------
# 4. PRIORITY ACTIONS
# -------------------------------------------------------------
render_section_header("Priority Actions", "Immediate decision recommendations requiring replenishment.")

top_cat = None
if len(snap) and "category" in snap.columns:
    cat_risk = snap[snap["health"].isin([HEALTH_CRITICAL, HEALTH_AT_RISK])]["category"].value_counts()
    top_cat = cat_risk.idxmax() if len(cat_risk) else None

trend_word = "trending upward" if (demand_growth or 0) >= 0 else "softening"
insight_bullets = [
    f"Demand trajectory is **{trend_word}** ({growth_str or 'stable'} over the trailing 28 days).",
    f"**{low_stock} product lines** are at critical or high stockout risk before supplier lead times elapse.",
    f"Inventory vulnerability is most heavily concentrated in the **{top_cat or 'General'}** category.",
    f"**{reorder_count} replenishment purchase orders** are recommended today to maintain target service levels.",
]
render_insight_card("Executive Intelligence Briefing", insight_bullets, urgency="high" if low_stock > 3 else "normal")

if has_inv and len(snap):
    urgent_pids = snap[snap["should_reorder"]].sort_values("days_to_stockout", ascending=True).head(3)
    if not urgent_pids.empty:
        st.write("**Top Immediate Reorders Required:**")
        for _, u_row in urgent_pids.iterrows():
            pid = u_row["product_id"]
            p_name = u_row["product_name"]
            p_series = get_daily_series(df, pid)
            rec = build_recommendation(
                pid, p_name, p_series["demand"], None,
                u_row["current_stock"], u_row["lead_time_days"], settings
            )
            render_recommendation_card(
                product_name=p_name,
                risk_level=rec.stockout_risk,
                current_stock=rec.current_stock,
                expected_demand=rec.avg_daily_demand * rec.lead_time_days,
                safety_stock=rec.safety_stock,
                reorder_point=rec.reorder_point,
                recommended_order_qty=rec.recommended_order_qty,
                why_reason=rec.explanation,
            )
        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 2])
        with col_btn2:
            if st.button("View Full Recommendations Catalog →", type="secondary", use_container_width=True):
                st.switch_page("pages/recommendations.py")
