"""Thin wrappers around scikit-learn / xgboost regressors used for demand
forecasting. All models are trained on engineered tabular features and
predict one-step-ahead demand; multi-day horizons are produced by recursive
prediction (predictor.py). ARIMA is handled separately (forecasting/arima.py)
since it is a genuine univariate time-series model, not a tabular regressor —
it is not constructed here, only listed in `available_models`.
"""
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from forecasting.arima import arima_available

try:
    from xgboost import XGBRegressor
    HAS_XGB = True
except ImportError:
    HAS_XGB = False


def get_model(name: str):
    if name == "Linear Regression":
        return LinearRegression()
    if name == "Random Forest":
        return RandomForestRegressor(n_estimators=200, max_depth=8, random_state=42, n_jobs=-1)
    if name == "XGBoost" and HAS_XGB:
        return XGBRegressor(n_estimators=200, max_depth=5, learning_rate=0.05,
                             random_state=42, verbosity=0)
    raise ValueError(f"Unknown or unavailable model: {name}")


def available_models(n_history_days: int, min_ml_days: int) -> list:
    """Choose which models are sensible given the amount of history available —
    do not blindly run expensive models against sparse data."""
    models = ["Naive", "Moving Average", "Seasonal Naive"]
    if arima_available(n_history_days):
        models.append("ARIMA")
    if n_history_days >= min_ml_days:
        models.append("Linear Regression")
    if n_history_days >= min_ml_days * 1.5:
        models.append("Random Forest")
    if n_history_days >= min_ml_days * 2 and HAS_XGB:
        models.append("XGBoost")
    return models
