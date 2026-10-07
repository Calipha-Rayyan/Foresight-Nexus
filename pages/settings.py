"""FORESIGHT Nexus — Configuration & Calibration Settings.

Allows operators to tune forecast horizons, machine-learning data thresholds,
service-level safety stock multipliers (Z-scores), and risk warning triggers.
"""
import streamlit as st
from core.config import Settings
from database.repositories import SettingsRepository
from ui.headers import render_page_header, render_section_header
from utils.logging import log_error

render_page_header(
    "Settings & Model Calibration",
    "Configure forecasting assumptions, safety stock buffers, and catalog risk thresholds.",
    meta_items=["Zero External Telemetry", "100% Local Execution", "State Persistence"]
)

s = st.session_state["settings"]

render_section_header("Forecasting Parameters", "Configure model horizon length and machine learning eligibility criteria.")
col_f1, col_f2 = st.columns(2)
with col_f1:
    horizon = st.slider(
        "Default Forecast Horizon (Days)",
        min_value=7, max_value=90, value=s.forecast_horizon_days,
        help="Default forward horizon for Command Center and Forecast Studio."
    )
    min_ml = st.slider(
        "Minimum History Required for ML Models (Days)",
        min_value=30, max_value=180, value=s.min_history_days_for_ml,
        help="SKUs with history below this threshold automatically fall back to baseline models."
    )

with col_f2:
    folds = st.slider(
        "Backtest Cross-Validation Folds",
        min_value=1, max_value=5, value=s.backtest_folds,
        help="Number of non-overlapping rolling evaluation splits used in model selection."
    )
    bt_horizon = st.slider(
        "Backtest Evaluation Window (Days)",
        min_value=7, max_value=30, value=s.backtest_horizon_days,
        help="Held-out forward evaluation period for each backtest split."
    )

render_section_header("Inventory & Service Level Assumptions", "Tune buffer sizing and supplier lead-time defaults.")
col_i1, col_i2 = st.columns(2)
with col_i1:
    lead_time = st.slider(
        "Default Supplier Lead Time (Days)",
        min_value=1, max_value=45, value=s.default_lead_time_days,
        help="Used as fallback when supplier lead time is unmapped in the dataset."
    )
with col_i2:
    z = st.slider(
        "Service Level Factor (Z-Score)",
        min_value=1.0, max_value=2.5, value=s.service_level_z, step=0.05,
        help="Multiplied by standard deviation of lead-time demand to size safety stock. 1.65 ≈ 95% service level, 2.05 ≈ 98%."
    )

render_section_header("Risk Thresholds & Exposure Triggers", "Define days-of-coverage triggers for stockout and overstock alerts.")
col_r1, col_r2 = st.columns(2)
with col_r1:
    stockout_thresh = st.slider(
        "Stockout Exposure Threshold (Days of Coverage)",
        min_value=3, max_value=30, value=s.stockout_risk_days_threshold,
        help="Products with fewer days of projected coverage are flagged as Critical/High stockout risk."
    )
with col_r2:
    overstock_thresh = st.slider(
        "Overstock Warning Threshold (Days of Coverage)",
        min_value=30, max_value=180, value=s.overstock_days_threshold,
        help="Products with more days of projected coverage are flagged as Overstock Working Capital Lockup."
    )

st.write("")
if st.button("Save & Apply Platform Configuration", type="primary"):
    st.session_state["settings"] = Settings(
        forecast_horizon_days=horizon,
        default_lead_time_days=lead_time,
        service_level_z=z,
        stockout_risk_days_threshold=stockout_thresh,
        overstock_days_threshold=overstock_thresh,
        min_history_days_for_ml=min_ml,
        backtest_folds=folds,
        backtest_horizon_days=bt_horizon,
    )
    try:
        SettingsRepository.save(st.session_state["settings"].__dict__)
    except Exception as e:
        log_error("Failed to persist settings snapshot", e)
    st.success("✅ Configuration updated successfully. All parameters will apply to subsequent analytical passes.")

st.divider()
st.caption("🔒 **Security & Privacy:** FORESIGHT Nexus processes all telemetry locally within your session. No data is transmitted to external endpoints.")
