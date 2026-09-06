import streamlit as st
from core.config import Settings
from database.repositories import SettingsRepository
from utils.logging import log_error

st.title("Settings")
st.caption("Configure the assumptions FORESIGHT Nexus uses for forecasting, risk, and reordering.")

s = st.session_state["settings"]

st.markdown("### Forecasting")
horizon = st.slider("Default Forecast Horizon (days)", 7, 90, s.forecast_horizon_days,
                     help="Default number of days ahead shown on the Command Center outlook chart.")
min_ml = st.slider("Minimum history required for ML models (days)", 30, 180, s.min_history_days_for_ml,
                    help="Products with less history than this fall back to baseline models — ML needs enough data to learn patterns reliably.")
folds = st.slider("Backtest folds", 1, 5, s.backtest_folds, help="Number of rolling train/test splits used to evaluate each model.")
bt_horizon = st.slider("Backtest horizon (days)", 7, 30, s.backtest_horizon_days, help="Length of each held-out evaluation window.")

st.markdown("### Inventory")
lead_time = st.slider("Default Lead Time (days)", 1, 30, s.default_lead_time_days,
                       help="Used when a product's supplier lead time is not present in the uploaded data.")
z = st.slider("Service Level (Z-score)", 1.0, 2.5, s.service_level_z, step=0.05,
              help="Higher = more safety stock, lower stockout probability. 1.65 ≈ 95% service level.")

st.markdown("### Risk Thresholds")
stockout_thresh = st.slider("Stockout Risk Threshold (days of coverage)", 3, 30, s.stockout_risk_days_threshold,
                             help="Products with fewer days of coverage than this are flagged at risk.")
overstock_thresh = st.slider("Overstock Threshold (days of coverage)", 30, 180, s.overstock_days_threshold,
                              help="Products with more days of coverage than this are flagged as overstocked.")

if st.button("Save Settings", type="primary"):
    st.session_state["settings"] = Settings(
        forecast_horizon_days=horizon, default_lead_time_days=lead_time, service_level_z=z,
        stockout_risk_days_threshold=stockout_thresh, overstock_days_threshold=overstock_thresh,
        min_history_days_for_ml=min_ml, backtest_folds=folds, backtest_horizon_days=bt_horizon,
    )
    try:
        SettingsRepository.save(st.session_state["settings"].__dict__)
    except Exception as e:
        log_error("Failed to persist settings snapshot", e)
    st.success("Settings saved. They will apply the next time a page recalculates.")

st.divider()
st.caption("FORESIGHT Nexus never sends your dataset to external APIs — all processing runs locally in this Streamlit session.")
