import streamlit as st
import pandas as pd
from forecasting.features import build_daily_series
from forecasting.evaluator import backtest_models, select_best_model
from forecasting.predictor import forecast as run_forecast
from forecasting.models import available_models


@st.cache_data(show_spinner=False)
def get_daily_series(df: pd.DataFrame, product_id: str) -> pd.DataFrame:
    return build_daily_series(df, product_id)


@st.cache_data(show_spinner=False)
def get_backtest_summary(series: pd.DataFrame, model_names: tuple, horizon: int, folds: int) -> dict:
    return backtest_models(series, list(model_names), horizon=horizon, folds=folds)


@st.cache_data(show_spinner=False)
def get_forecast(series: pd.DataFrame, model_name: str, horizon: int) -> pd.DataFrame:
    return run_forecast(series, model_name, horizon)


def best_model_for_product(series: pd.DataFrame, settings) -> tuple:
    n_days = len(series)
    candidates = tuple(available_models(n_days, settings.min_history_days_for_ml))
    summary = get_backtest_summary(series, candidates, settings.backtest_horizon_days, settings.backtest_folds)
    best_name, reason = select_best_model(summary)
    if best_name is None:
        best_name = "Moving Average"
        reason = "Insufficient history for backtesting — defaulted to a moving-average baseline."
    return best_name, reason, summary
