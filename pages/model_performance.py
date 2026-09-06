import streamlit as st
import pandas as pd
from core.state import has_data
from ui.components import empty_state, section_title, kpi_card
from utils.pipeline import get_daily_series, best_model_for_product
from visualizations.forecast_charts import create_forecast_accuracy_chart
from forecasting.models import available_models

st.title("Model Performance")

if not has_data():
    empty_state("No dataset loaded", "Upload your sales history or load the demo dataset to evaluate models.")
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]

product_names = df[["product_id", "product_name"]].drop_duplicates()
label = st.selectbox("Product", (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist())
product_id = label.split("(")[-1].rstrip(")")

series = get_daily_series(df, product_id)
candidates = available_models(len(series), settings.min_history_days_for_ml)
with st.spinner("Backtesting candidate models..."):
    best_name, reason, summary = best_model_for_product(series, settings)

if not summary:
    st.warning("Not enough history for this product to run a backtest.")
    st.stop()

st.markdown(f"""
<div class="fn-card" style="text-align:center; padding:1.4rem;">
    <div class="fn-kpi-label">Best Performing Model</div>
    <div class="fn-kpi-value" style="font-size:2.2rem;">{best_name}</div>
</div>
""", unsafe_allow_html=True)
st.write("")

c1, c2, c3, c4 = st.columns(4)
best = summary[best_name]
with c1: kpi_card("MAE", f"{best['MAE']}")
with c2: kpi_card("RMSE", f"{best['RMSE']}")
with c3: kpi_card("WAPE", f"{best['WAPE']}%" if best['WAPE'] is not None else "N/A")
with c4: kpi_card("Backtest Folds Used", f"{best['folds_used']}")

st.info(f"**Why this model was selected:** {reason}")

section_title("Model Comparison")
rows = []
for name in candidates:
    if name in summary:
        m = summary[name]
        rows.append({"Model": name, "Status": "Validated", "MAE": m["MAE"], "RMSE": m["RMSE"],
                     "WAPE (%)": m["WAPE"], "MAPE (%)": m["MAPE"], "Backtest Folds": m["folds_used"]})
    else:
        rows.append({"Model": name, "Status": "Unavailable for this series", "MAE": None, "RMSE": None,
                     "WAPE (%)": None, "MAPE (%)": None, "Backtest Folds": 0})
comp_df = pd.DataFrame(rows).sort_values("WAPE (%)", na_position="last")
comp_df.insert(0, "Rank", range(1, len(comp_df) + 1))
st.dataframe(comp_df, use_container_width=True, hide_index=True)
st.caption("Metrics are averaged across time-aware backtest folds (train on the past, evaluate on a later held-out window — never shuffled). "
           "\"Unavailable\" means the model's minimum data or convergence requirements weren't met for this specific product — it was skipped, not forced.")

if comp_df["WAPE (%)"].notna().any():
    section_title("Model Comparison Chart")
    st.plotly_chart(create_forecast_accuracy_chart(comp_df.dropna(subset=["WAPE (%)"])), use_container_width=True)
else:
    st.caption("WAPE unavailable for these models (only occurs when this window has zero total actual demand).")
