"""Feature engineering for per-product demand forecasting.

Each feature's purpose:
- lag_N: demand N days ago — captures short/medium-term autocorrelation.
- rolling_mean_N: N-day average demand — smooths noise, captures level.
- rolling_std_N: N-day demand volatility — feeds confidence estimation.
- day_of_week / week / month / quarter: calendar seasonality signals.
- trend: linear time index — lets models capture drift.
"""
import pandas as pd
import numpy as np


def build_daily_series(df: pd.DataFrame, product_id: str) -> pd.DataFrame:
    """Returns a complete daily (no gaps) demand series for one product."""
    sub = df[df["product_id"] == product_id].groupby("date", as_index=False)["quantity"].sum()
    sub = sub.set_index("date").asfreq("D", fill_value=0).rename(columns={"quantity": "demand"})
    return sub.reset_index()


def engineer_features(series: pd.DataFrame) -> pd.DataFrame:
    """series: DataFrame with columns [date, demand], daily frequency, no gaps."""
    out = series.copy().sort_values("date").reset_index(drop=True)

    for lag in (1, 7, 14, 28):
        out[f"lag_{lag}"] = out["demand"].shift(lag)

    for win in (7, 14, 28):
        out[f"rolling_mean_{win}"] = out["demand"].shift(1).rolling(win).mean()
    for win in (7, 28):
        out[f"rolling_std_{win}"] = out["demand"].shift(1).rolling(win).std()

    out["day_of_week"] = out["date"].dt.dayofweek
    out["week"] = out["date"].dt.isocalendar().week.astype(int)
    out["month"] = out["date"].dt.month
    out["quarter"] = out["date"].dt.quarter
    out["trend"] = np.arange(len(out))

    return out


FEATURE_COLUMNS = [
    "lag_1", "lag_7", "lag_14", "lag_28",
    "rolling_mean_7", "rolling_mean_14", "rolling_mean_28",
    "rolling_std_7", "rolling_std_28",
    "day_of_week", "week", "month", "quarter", "trend",
]
