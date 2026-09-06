"""Naive and moving-average baseline forecasters."""
import numpy as np
import pandas as pd


def naive_forecast(history: pd.Series, horizon: int) -> np.ndarray:
    """Repeats the last observed value for the whole horizon."""
    last = history.iloc[-1] if len(history) else 0.0
    return np.full(horizon, last, dtype=float)


def moving_average_forecast(history: pd.Series, horizon: int, window: int = 7) -> np.ndarray:
    avg = history.tail(window).mean() if len(history) else 0.0
    return np.full(horizon, avg, dtype=float)


def seasonal_naive_forecast(history: pd.Series, horizon: int, season: int = 7) -> np.ndarray:
    """Repeats the same weekday's demand pattern from the last full season."""
    if len(history) < season:
        return naive_forecast(history, horizon)
    last_season = history.tail(season).values
    reps = int(np.ceil(horizon / season))
    return np.tile(last_season, reps)[:horizon]
