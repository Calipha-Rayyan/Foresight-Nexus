"""FORESIGHT Nexus — Forecast Studio Workspace.

Interactive forecasting workspace supporting Naive, Moving Average, Linear Regression,
Random Forest, XGBoost, and ARIMA with automated cross-validation and fallback handling.
"""
import streamlit as st
import pandas as pd
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_empty_state, render_forecast_summary_card
from ui.tables import style_dataframe
from visualizations.forecast_charts import (
    create_demand_forecast_chart,
    create_actual_vs_forecast_chart,
    create_forecast_accuracy_chart,
)
from utils.pipeline import get_daily_series, get_forecast, best_model_for_product
from forecasting.models import available_models
from forecasting.predictor import confidence_label
from recommendations.explanations import forecast_confidence_explanation, insufficient_data_explanation
from forecasting.evaluator import backtest_models

render_page_header(
    "Forecast Studio",
    "Generate, calibrate, and compare forward demand predictions across statistical and machine learning models.",
    meta_items=["Multi-Model Backtesting", "ARIMA Time-Series", "Confidence Bounds (80% CI)"]
)

if not has_data():
    render_empty_state(
        "No Dataset Connected",
        "Upload sales history in Data Lab or load the demo dataset to calibrate demand models.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]

# -------------------------------------------------------------
# Control Bar
# -------------------------------------------------------------
with st.container():
    c1, c2, c3, c4, c5 = st.columns([1.5, 2.5, 1.2, 2.2, 1.4])
    with c1:
        cat_options = ["All Categories"] + sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else ["All Categories"]
        category = st.selectbox("Category", cat_options)
    
    prod_options = df if category == "All Categories" or "category" not in df.columns else df[df["category"] == category]
    vol = prod_options.groupby("product_id")["quantity"].sum()
    product_names = prod_options[["product_id", "product_name"]].drop_duplicates().copy()
    product_names["vol"] = product_names["product_id"].map(vol).fillna(0)
    product_names = product_names.sort_values("vol", ascending=False)
    
    with c2:
        prod_labels = (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist()
        product_label = st.selectbox("Product", prod_labels)
        product_id = product_label.split("(")[-1].rstrip(")")
        selected_prod_name = product_label.split("  (")[0]

    with c3:
        horizon = st.selectbox("Horizon", [7, 14, 30, 60, 90], index=2, format_func=lambda h: f"{h} Days")

    with c4:
        series_pre = get_daily_series(df, product_id)
        n_days_hist = len(series_pre)
        available_cand = available_models(n_days_hist, settings.min_history_days_for_ml)
        model_choices = ["Auto (Best Backtested Model)"] + available_cand
        model_choice = st.selectbox("Model Architecture", model_choices)

    with c5:
        st.write("")
        st.write("")
        run_btn = st.button("Generate Forecast", type="primary", use_container_width=True)
        if run_btn:
            st.session_state["_run_forecast"] = True

# -------------------------------------------------------------
# Forecast Generation & Workspace
# -------------------------------------------------------------
if st.session_state.get("_run_forecast", True):
    series = get_daily_series(df, product_id)
    n_days_hist = len(series)

    if n_days_hist < 14:
        st.warning(insufficient_data_explanation(n_days_hist, settings.min_history_days_for_ml))
        st.stop()

    with st.spinner("Calibrating time-series models and computing prediction intervals..."):
        if model_choice.startswith("Auto"):
            model_name, reason, summary = best_model_for_product(series, settings)
        else:
            model_name = model_choice
            reason = "Manually specified by operator."
            # Backtest manually specified model alongside others for comparison
            summary = backtest_models(series, [model_name, "Moving Average"], horizon=settings.backtest_horizon_days, folds=settings.backtest_folds)

        fc = get_forecast(series, model_name, horizon)

    # Professional ARIMA Fallback Handling
    if model_name == "ARIMA":
        recent_std = series["demand"].tail(28).std()
        too_short = n_days_hist < 30
        constant = pd.notna(recent_std) and recent_std == 0
        if too_short or constant:
            st.info(
                "ℹ️ **ARIMA Notice:** ARIMA was not suitable for this series due to short history or zero variance. "
                "A validated baseline model was used instead."
            )
            model_name = "Moving Average (ARIMA fallback)"

    band_pct = float(((fc["upper"] - fc["lower"]) / fc["forecast"].replace(0, 1)).mean() * 100)
    conf = confidence_label(band_pct)
    range_str = f"{fc['lower'].sum():,.0f} – {fc['upper'].sum():,.0f}"

    # Forecast Summary Card
    render_forecast_summary_card(
        model_name=model_name,
        forecast_units=float(fc["forecast"].sum()),
        expected_range=range_str,
        confidence=conf,
        reason=reason,
    )

    # Hero Forecast Chart
    render_section_header("Demand Forecast", f"{selected_prod_name} forward demand outlook with 80% confidence interval.")
    fig = create_demand_forecast_chart(
        series,
        fc,
        product_name=selected_prod_name,
        history_tail_days=120,
    )
    st.plotly_chart(fig, use_container_width=True)

    # Backtest Evaluation & Validation Section
    render_section_header("Model Evaluation & Backtest Validation", "Comparing predictive accuracy on held-out historical windows.")
    col_eval1, col_eval2 = st.columns([1, 1])

    with col_eval1:
        # Evaluation rows
        eval_rows = []
        for name in available_cand:
            if name in summary:
                m = summary[name]
                eval_rows.append({
                    "Model": name,
                    "Status": "Validated",
                    "MAE": round(m["MAE"], 2),
                    "RMSE": round(m["RMSE"], 2),
                    "WAPE (%)": round(m["WAPE"], 1) if m["WAPE"] is not None else None,
                })
            else:
                eval_rows.append({
                    "Model": name,
                    "Status": "Unavailable",
                    "MAE": None,
                    "RMSE": None,
                    "WAPE (%)": None,
                })
        comp_df = pd.DataFrame(eval_rows).sort_values("WAPE (%)", na_position="last")
        st.write("**Cross-Validation Leaderboard:**")
        style_dataframe(comp_df)

    with col_eval2:
        if not comp_df.dropna(subset=["WAPE (%)"]).empty:
            st.plotly_chart(create_forecast_accuracy_chart(comp_df), use_container_width=True)
        else:
            st.caption("Cross-validation metrics unavailable for this horizon.")

    with st.expander("Detailed Forecast Tabular Schedule"):
        fc_disp = fc.copy()
        num_cols = fc_disp.select_dtypes(include="number").columns
        fc_disp[num_cols] = fc_disp[num_cols].round(1)
        style_dataframe(fc_disp)
else:
    render_section_header("Forecast Workspace Standing By", "Configure parameters in the control bar above and click 'Generate Forecast'.")
