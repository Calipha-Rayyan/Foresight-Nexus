import pandas as pd
import numpy as np
from forecasting.features import engineer_features, FEATURE_COLUMNS
from forecasting.baseline import naive_forecast, moving_average_forecast, seasonal_naive_forecast
from forecasting.evaluator import backtest_models, select_best_model


def _make_series(n=120):
    dates = pd.date_range("2026-01-01", periods=n)
    demand = np.round(20 + 5 * np.sin(np.arange(n) / 7) + np.random.default_rng(1).normal(0, 1, n)).clip(0)
    return pd.DataFrame({"date": dates, "demand": demand})


def test_engineer_features_has_expected_columns():
    series = _make_series()
    feat = engineer_features(series)
    for col in FEATURE_COLUMNS:
        assert col in feat.columns


def test_naive_forecast_repeats_last_value():
    hist = pd.Series([1, 2, 3, 10])
    fc = naive_forecast(hist, 5)
    assert (fc == 10).all()


def test_moving_average_forecast_uses_window():
    hist = pd.Series([10, 20, 30])
    fc = moving_average_forecast(hist, 3, window=3)
    assert fc[0] == 20


def test_seasonal_naive_forecast_repeats_pattern():
    hist = pd.Series([1, 2, 3, 4, 5, 6, 7])
    fc = seasonal_naive_forecast(hist, 7, season=7)
    assert list(fc) == [1, 2, 3, 4, 5, 6, 7]


def test_backtest_does_not_shuffle_and_returns_metrics():
    series = _make_series(150)
    summary = backtest_models(series, ["Naive", "Moving Average"], horizon=7, folds=2)
    assert "Naive" in summary
    assert summary["Naive"]["MAE"] >= 0


def test_select_best_model_picks_lowest_wape():
    summary = {
        "A": {"MAE": 5, "RMSE": 6, "WAPE": 20, "MAPE": 25, "folds_used": 2},
        "B": {"MAE": 4, "RMSE": 5, "WAPE": 10, "MAPE": 15, "folds_used": 2},
    }
    best, reason = select_best_model(summary)
    assert best == "B"
    assert "WAPE=10%" in reason


def test_select_best_model_reason_honest_when_wape_unavailable():
    # Zero-demand backtest window: WAPE is undefined (division by zero denom),
    # selection must fall back to MAE — and the reason text must say so, not
    # claim a WAPE value that doesn't exist.
    summary = {
        "Naive": {"MAE": 0.0, "RMSE": 0.0, "WAPE": None, "MAPE": None, "folds_used": 3},
    }
    best, reason = select_best_model(summary)
    assert best == "Naive"
    assert "None%" not in reason
    assert "MAE" in reason
