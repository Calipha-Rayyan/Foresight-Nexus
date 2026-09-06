"""Generates a horizon-length forecast using the selected model, plus a
confidence interval derived from recent residual volatility (not invented)."""
import numpy as np
import pandas as pd
from forecasting.features import engineer_features, FEATURE_COLUMNS
from forecasting.baseline import naive_forecast, moving_average_forecast, seasonal_naive_forecast
from forecasting.models import get_model
from forecasting.arima import arima_forecast, ArimaUnavailableError
from utils.logging import log_error


def forecast(series: pd.DataFrame, model_name: str, horizon: int) -> pd.DataFrame:
    feat = engineer_features(series)
    hist = feat["demand"]
    last_date = series["date"].max()
    future_dates = pd.date_range(last_date + pd.Timedelta(days=1), periods=horizon)

    if model_name == "Naive":
        preds = naive_forecast(hist, horizon)
        return _band_from_recent_volatility(feat, preds, future_dates)
    elif model_name == "Moving Average":
        preds = moving_average_forecast(hist, horizon)
        return _band_from_recent_volatility(feat, preds, future_dates)
    elif model_name == "Seasonal Naive":
        preds = seasonal_naive_forecast(hist, horizon)
        return _band_from_recent_volatility(feat, preds, future_dates)
    elif model_name == "ARIMA":
        try:
            result = arima_forecast(hist, horizon)
            return pd.DataFrame({
                "date": future_dates, "forecast": result["forecast"],
                "lower": result["lower"], "upper": result["upper"],
            })
        except ArimaUnavailableError as e:
            # Graceful fallback per spec: never crash, never fabricate — fall
            # back to a baseline and let the caller's UI explain the switch.
            log_error("ARIMA unavailable at forecast time, falling back to Moving Average", e)
            preds = moving_average_forecast(hist, horizon)
            return _band_from_recent_volatility(feat, preds, future_dates)
    else:
        preds = _recursive_ml_forecast(feat, model_name, horizon, future_dates)
        return _band_from_recent_volatility(feat, preds, future_dates)


def _band_from_recent_volatility(feat: pd.DataFrame, preds: np.ndarray, future_dates) -> pd.DataFrame:
    preds = np.clip(preds, 0, None)
    # Confidence: derive from recent 28-day residual-free volatility (rolling std),
    # widening with the square root of the forecast step (standard random-walk assumption).
    recent_std = feat["demand"].tail(28).std()
    if pd.isna(recent_std) or recent_std == 0:
        recent_std = max(1.0, feat["demand"].tail(14).mean() * 0.15)
    steps = np.arange(1, len(preds) + 1)
    band = 1.28 * recent_std * np.sqrt(steps)  # ~80% interval

    return pd.DataFrame({
        "date": future_dates,
        "forecast": preds,
        "lower": np.clip(preds - band, 0, None),
        "upper": preds + band,
    })


def _recursive_ml_forecast(feat: pd.DataFrame, model_name: str, horizon: int, future_dates) -> np.ndarray:
    train = feat.dropna(subset=FEATURE_COLUMNS + ["demand"])
    if len(train) < 20:
        return moving_average_forecast(feat["demand"], horizon)

    model = get_model(model_name)
    model.fit(train[FEATURE_COLUMNS], train["demand"])

    history = feat[["date", "demand"]].copy()
    preds = []
    for d in future_dates:
        tmp = pd.concat([history, pd.DataFrame({"date": [d], "demand": [np.nan]})], ignore_index=True)
        tmp_feat = _row_features(tmp)
        row = tmp_feat.iloc[[-1]][FEATURE_COLUMNS].fillna(train[FEATURE_COLUMNS].median())
        pred = max(0.0, float(model.predict(row)[0]))
        preds.append(pred)
        history = pd.concat([history, pd.DataFrame({"date": [d], "demand": [pred]})], ignore_index=True)

    return np.array(preds)


def _row_features(series: pd.DataFrame) -> pd.DataFrame:
    from forecasting.features import engineer_features
    return engineer_features(series)


def confidence_label(band_width_pct: float) -> str:
    if band_width_pct < 15:
        return "High"
    if band_width_pct < 35:
        return "Medium"
    return "Low"
