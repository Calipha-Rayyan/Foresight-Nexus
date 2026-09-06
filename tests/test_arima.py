import numpy as np
import pandas as pd
import pytest
from forecasting.arima import arima_forecast, arima_available, ArimaUnavailableError, MIN_ARIMA_HISTORY_DAYS
from forecasting.models import available_models
from forecasting.evaluator import backtest_models
from forecasting.predictor import forecast as run_forecast
from forecasting.features import build_daily_series


def _synthetic_series(n=120, seed=3):
    rng = np.random.default_rng(seed)
    dates = pd.date_range("2026-01-01", periods=n)
    values = 20 + 4 * np.sin(np.arange(n) / 6) + rng.normal(0, 1.5, n)
    return pd.Series(np.clip(values, 0, None), index=range(n))


def test_arima_available_respects_minimum_history():
    assert arima_available(MIN_ARIMA_HISTORY_DAYS) is True
    assert arima_available(MIN_ARIMA_HISTORY_DAYS - 1) is False


def test_arima_forecast_valid_series_returns_expected_shape():
    hist = _synthetic_series(120)
    result = arima_forecast(hist, horizon=14)
    assert len(result["forecast"]) == 14
    assert len(result["lower"]) == 14
    assert len(result["upper"]) == 14
    assert (result["upper"] >= result["lower"]).all()
    assert (result["forecast"] >= 0).all()
    assert isinstance(result["order"], tuple) and len(result["order"]) == 3


def test_arima_forecast_insufficient_history_raises():
    short_hist = pd.Series([5, 6, 7, 8, 9])
    with pytest.raises(ArimaUnavailableError):
        arima_forecast(short_hist, horizon=7)


def test_arima_forecast_constant_series_raises():
    constant_hist = pd.Series([10.0] * 60)
    with pytest.raises(ArimaUnavailableError):
        arima_forecast(constant_hist, horizon=7)


def test_arima_forecast_nan_series_raises():
    bad_hist = pd.Series([5, 6, np.nan, 8] * 20)
    with pytest.raises(ArimaUnavailableError):
        arima_forecast(bad_hist, horizon=7)


def test_available_models_includes_arima_when_history_sufficient():
    models = available_models(n_history_days=120, min_ml_days=90)
    assert "ARIMA" in models


def test_available_models_excludes_arima_when_history_short():
    models = available_models(n_history_days=10, min_ml_days=90)
    assert "ARIMA" not in models


def test_backtest_models_includes_arima_without_crashing():
    dates = pd.date_range("2026-01-01", periods=150)
    demand = np.clip(20 + 4 * np.sin(np.arange(150) / 6) + np.random.default_rng(1).normal(0, 1, 150), 0, None)
    series = pd.DataFrame({"date": dates, "demand": demand})
    summary = backtest_models(series, ["Naive", "ARIMA"], horizon=7, folds=2)
    # ARIMA may or may not converge for every fold, but must never raise —
    # either it's present with real metrics, or gracefully absent.
    if "ARIMA" in summary:
        assert summary["ARIMA"]["MAE"] >= 0


def test_predictor_forecast_arima_end_to_end():
    dates = pd.date_range("2026-01-01", periods=120)
    demand = np.clip(20 + 4 * np.sin(np.arange(120) / 6) + np.random.default_rng(2).normal(0, 1, 120), 0, None)
    series = pd.DataFrame({"date": dates, "demand": demand})
    fc = run_forecast(series, "ARIMA", horizon=14)
    assert len(fc) == 14
    assert (fc["forecast"] >= 0).all()
    assert (fc["upper"] >= fc["lower"]).all()


def test_predictor_forecast_arima_falls_back_gracefully_on_short_history():
    dates = pd.date_range("2026-01-01", periods=10)
    demand = [5, 6, 7, 5, 6, 7, 5, 6, 7, 5]
    series = pd.DataFrame({"date": dates, "demand": demand})
    # Must not raise, even though ARIMA itself would refuse this series.
    fc = run_forecast(series, "ARIMA", horizon=7)
    assert len(fc) == 7
    assert (fc["forecast"] >= 0).all()
