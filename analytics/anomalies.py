"""Statistical anomaly detection on a daily demand series. Reports only
statistical facts ('unusual spike/drop detected'), never causal claims."""
import numpy as np
import pandas as pd


def detect_anomalies(series: pd.DataFrame, window: int = 14, z_thresh: float = 2.5) -> pd.DataFrame:
    """series: [date, demand]. Returns rows flagged as anomalous with a z-score
    computed against a trailing rolling mean/std (excludes the point itself)."""
    s = series.copy().sort_values("date").reset_index(drop=True)
    roll_mean = s["demand"].shift(1).rolling(window).mean()
    roll_std = s["demand"].shift(1).rolling(window).std()
    # When recent history has zero variability, fall back to a minimum std floor
    # (proportional to the mean) so a genuine deviation is still detectable.
    floor = (roll_mean.abs() * 0.05).clip(lower=0.5)
    roll_std_safe = roll_std.where(roll_std > 0, floor)
    s["z_score"] = (s["demand"] - roll_mean) / roll_std_safe
    s["anomaly"] = s["z_score"].abs() >= z_thresh
    s["anomaly_type"] = np.where(s["z_score"] >= z_thresh, "Unusual demand spike detected",
                          np.where(s["z_score"] <= -z_thresh, "Unusual demand drop detected", None))
    return s[s["anomaly"] == True][["date", "demand", "z_score", "anomaly_type"]]
