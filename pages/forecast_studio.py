import streamlit as st
import pandas as pd
from core.state import has_data
from ui.components import empty_state, kpi_card
from visualizations.forecast_charts import create_demand_forecast_chart
from utils.pipeline import get_daily_series, get_forecast, best_model_for_product
from forecasting.models import available_models
from forecasting.predictor import confidence_label
from recommendations.explanations import forecast_confidence_explanation, insufficient_data_explanation

st.title("Forecast Studio")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to generate forecasts.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]

c1, c2, c3, c4 = st.columns(4)
with c1:
    category = st.selectbox("Category", ["All"] + sorted(df["category"].dropna().unique().tolist()) if "category" in df.columns else ["All"])
prod_options = df if category == "All" or "category" not in df.columns else df[df["category"] == category]
product_names = prod_options[["product_id", "product_name"]].drop_duplicates()
with c2:
    product_label = st.selectbox("Product", (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist())
product_id = product_label.split("(")[-1].rstrip(")")
with c3:
    horizon = st.selectbox("Forecast Horizon", [7, 14, 30, 60, 90], index=2)
with c4:
    n_days_hist = len(get_daily_series(df, product_id))
    model_choices = ["Auto (best backtested model)"] + available_models(n_days_hist, settings.min_history_days_for_ml)
    model_choice = st.selectbox("Model", model_choices)

if st.button("Generate Forecast", type="primary"):
    st.session_state["_run_forecast"] = True

if st.session_state.get("_run_forecast"):
    series = get_daily_series(df, product_id)
    n_days_hist = len(series)

    if n_days_hist < 14:
        st.warning(insufficient_data_explanation(n_days_hist, settings.min_history_days_for_ml))
        st.stop()

    with st.spinner("Evaluating models and generating forecast..."):
        if model_choice.startswith("Auto"):
            model_name, reason, summary = best_model_for_product(series, settings)
        else:
            model_name = model_choice
            reason = "Manually selected by user."
            if model_name == "ARIMA":
                st.caption("ARIMA selected — the model will be fit to this product's historical demand before generating the forecast.")
        fc = get_forecast(series, model_name, horizon)

    # If ARIMA was requested but the historical series wasn't suitable, the
    # predictor silently falls back to Moving Average — surface that honestly
    # rather than letting the KPI card claim "ARIMA" for a baseline result.
    if model_name == "ARIMA":
        recent_std = series["demand"].tail(28).std()
        too_short = n_days_hist < 30
        constant = pd.notna(recent_std) and recent_std == 0
        if too_short or constant:
            st.warning("ARIMA was not suitable for this product's available history. A baseline forecasting model was used instead.")
            model_name = "Moving Average (ARIMA fallback)"

    if n_days_hist < settings.min_history_days_for_ml:
        st.info(insufficient_data_explanation(n_days_hist, settings.min_history_days_for_ml))

    band_pct = float(((fc["upper"] - fc["lower"]) / fc["forecast"].replace(0, 1)).mean() * 100)
    conf = confidence_label(band_pct)

    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Model Used", model_name)
    with c2: kpi_card("Forecast (Horizon Total)", f"{fc['forecast'].sum():,.0f} units")
    with c3: kpi_card("Expected Range", f"{fc['lower'].sum():,.0f}–{fc['upper'].sum():,.0f}")
    with c4: kpi_card("Forecast Confidence", conf)

    st.info(f"**Why this model:** {reason}")
    st.caption(forecast_confidence_explanation(conf, band_pct))

    fig = create_demand_forecast_chart(series, fc, history_tail_days=120)
    st.plotly_chart(fig, use_container_width=True)

    with st.expander("Forecast data"):
        st.dataframe(fc.round(1), use_container_width=True, hide_index=True)
else:
    st.caption("Choose a product and horizon, then click Generate Forecast.")
