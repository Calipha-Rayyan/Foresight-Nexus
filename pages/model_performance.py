"""FORESIGHT Nexus — Model Performance & Evaluation Leaderboard.

Empirical evaluation engine: benchmarks candidate algorithms across held-out time-aware folds,
calculating MAE, RMSE, and WAPE to select the optimal model for each individual SKU.
"""
import streamlit as st
import pandas as pd
from core.state import has_data
from ui.headers import render_page_header, render_section_header
from ui.cards import render_empty_state, render_kpi_card
from ui.tables import style_dataframe
from utils.pipeline import get_daily_series, best_model_for_product
from visualizations.forecast_charts import create_forecast_accuracy_chart
from forecasting.models import available_models

render_page_header(
    "Model Performance",
    "Rigorous empirical evaluation and time-aware backtesting across candidate forecasting architectures.",
    meta_items=["Rolling Backtest Folds", "Zero Future-Leakage", "WAPE Ranking"]
)

if not has_data():
    render_empty_state(
        "No Active Dataset Connected",
        "Upload sales history in Data Lab or load the demo dataset to evaluate algorithm performance.",
        "Go to Data Lab",
        "pages/data_lab.py",
    )
    st.stop()

df = st.session_state["dataset"]
settings = st.session_state["settings"]

# Product Selector: sorted by historical volume for high-velocity default SKU
vol = df.groupby("product_id")["quantity"].sum()
product_names = df[["product_id", "product_name"]].drop_duplicates().copy()
product_names["vol"] = product_names["product_id"].map(vol).fillna(0)
product_names = product_names.sort_values("vol", ascending=False)
prod_labels = (product_names["product_name"] + "  (" + product_names["product_id"] + ")").tolist()
label = st.selectbox("Select Target SKU for Evaluation", prod_labels)
product_id = label.split("(")[-1].rstrip(")")
prod_name = label.split("  (")[0]

series = get_daily_series(df, product_id)
candidates = available_models(len(series), settings.min_history_days_for_ml)

with st.spinner(f"Executing rolling time-series backtest across candidate models for {prod_name}..."):
    best_name, reason, summary = best_model_for_product(series, settings)

if not summary:
    st.warning("⚠️ Insufficient historical series length to complete rolling backtesting folds.")
    st.stop()

# -------------------------------------------------------------
# Winning Model Showcase
# -------------------------------------------------------------
best = summary[best_name]

st.markdown(
    f'<div class="fn-card" style="margin-bottom:1.25rem; padding:1.25rem 1.5rem; border-color:#28B8FF;">'
    f'<div style="display:flex; justify-content:space-between; align-items:center; flex-wrap:wrap; gap:0.5rem;">'
    f'<div>'
    f'<span style="font-size:0.75rem; text-transform:uppercase; font-weight:700; color:#28B8FF; letter-spacing:0.05em;">Optimal Architecture Selected</span>'
    f'<h2 style="margin:0.2rem 0; font-size:1.85rem; font-weight:800; color:#FFFFFF;">{best_name}</h2>'
    f'<div style="color:#8B9BB4; font-size:0.85rem; max-width:680px;"><b>Selection Rationale:</b> {reason}</div>'
    f'</div>'
    f'</div>'
    f'</div>',
    unsafe_allow_html=True
)

c1, c2, c3, c4 = st.columns(4)
with c1:
    render_kpi_card("Mean Absolute Error (MAE)", f"{best['MAE']:.2f} units", context="Average absolute point error")
with c2:
    render_kpi_card("Root Mean Sq Error (RMSE)", f"{best['RMSE']:.2f}", context="Penalizes large outlier misses")
with c3:
    wape_str = f"{best['WAPE']:.1f}%" if best['WAPE'] is not None else "N/A"
    render_kpi_card("WAPE Error Rate", wape_str, status="Healthy" if (best['WAPE'] or 100) < 25 else "Watch", context="Weighted volume error rate")
with c4:
    render_kpi_card("Backtest Folds Evaluated", f"{best['folds_used']}", context=f"{settings.backtest_horizon_days}-day held-out windows")

# -------------------------------------------------------------
# Comparison Leaderboard
# -------------------------------------------------------------
render_section_header("Cross-Validation Leaderboard", "Exhaustive comparison across all candidate architectures evaluated on this SKU.")

rows = []
for name in candidates:
    if name in summary:
        m = summary[name]
        rows.append({
            "Model": name,
            "Architecture": name,
            "Validation Status": "Validated",
            "MAE": round(m["MAE"], 2),
            "RMSE": round(m["RMSE"], 2),
            "WAPE (%)": round(m["WAPE"], 1) if m["WAPE"] is not None else None,
            "MAPE (%)": round(m["MAPE"], 1) if m["MAPE"] is not None else None,
            "Evaluation Folds": m["folds_used"],
        })
    else:
        rows.append({
            "Model": name,
            "Architecture": name,
            "Validation Status": "Convergence / History Ineligible",
            "MAE": None,
            "RMSE": None,
            "WAPE (%)": None,
            "MAPE (%)": None,
            "Evaluation Folds": 0,
        })

comp_df = pd.DataFrame(rows).sort_values("WAPE (%)", na_position="last")
comp_df.insert(0, "Rank", range(1, len(comp_df) + 1))
style_dataframe(comp_df)

st.caption(
    "Metrics represent out-of-sample averages across rolling evaluation splits. "
    "Models marked 'Ineligible' either did not converge or the historical window did not meet the algorithm's minimum data threshold."
)

if comp_df["WAPE (%)"].notna().any():
    render_section_header("Error Rate Comparison (Lower is Better)")
    st.plotly_chart(create_forecast_accuracy_chart(comp_df.dropna(subset=["WAPE (%)"])), use_container_width=True)
