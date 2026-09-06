"""ARIMA forecasting, implemented as a genuine univariate time-series model
(statsmodels), not treated like a generic tabular regressor. Uses a small,
bounded set of (p,d,q) candidates rather than a large grid search, selecting
by AIC on the training window only (never touching the held-out test window
— that would be a second, subtler form of leakage even inside "model
selection").
"""
import warnings
import numpy as np
import pandas as pd

MIN_ARIMA_HISTORY_DAYS = 30

# Small, bounded candidate set — deliberately not an exhaustive grid search,
# per "keep it bounded and efficient" / must stay responsive in Streamlit.
_ORDER_CANDIDATES = [
    (1, 1, 1),
    (2, 1, 2),
    (1, 1, 0),
    (0, 1, 1),
    (2, 0, 2),
]


class ArimaUnavailableError(Exception):
    """Raised when ARIMA cannot be safely fit to this series — callers should
    catch this and fall back to another model, never surface it to the user
    as a raw traceback."""
    pass


def _validate_series(history: pd.Series) -> None:
    if history is None or len(history) < MIN_ARIMA_HISTORY_DAYS:
        raise ArimaUnavailableError(
            f"Insufficient history ({0 if history is None else len(history)} days; "
            f"needs at least {MIN_ARIMA_HISTORY_DAYS})."
        )
    if history.isna().any():
        raise ArimaUnavailableError("Series contains missing values.")
    if not np.isfinite(history.values).all():
        raise ArimaUnavailableError("Series contains non-finite values.")
    if history.std() == 0:
        raise ArimaUnavailableError("Series is constant — ARIMA offers no benefit over a naive forecast.")


def _fit_best_order(history: pd.Series):
    """Fits each bounded candidate order on the training window and keeps the
    lowest-AIC model that converges. AIC is computed only on the training
    data itself, so this selection step cannot leak information from any
    held-out evaluation window."""
    from statsmodels.tsa.arima.model import ARIMA

    best_fit, best_aic, best_order = None, np.inf, None
    for order in _ORDER_CANDIDATES:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                model = ARIMA(history.values, order=order)
                fit = model.fit()
            if np.isfinite(fit.aic) and fit.aic < best_aic:
                best_fit, best_aic, best_order = fit, fit.aic, order
        except Exception:
            continue  # this order didn't converge — try the next candidate

    if best_fit is None:
        raise ArimaUnavailableError("No ARIMA order configuration converged for this series.")
    return best_fit, best_order


def arima_forecast(history: pd.Series, horizon: int, alpha: float = 0.2) -> dict:
    """Returns {'forecast': np.ndarray, 'lower': np.ndarray, 'upper': np.ndarray,
    'order': (p,d,q)} or raises ArimaUnavailableError. `alpha` is the two-sided
    significance level for the confidence interval (0.2 -> 80%, matching the
    other models' interval convention in predictor.py)."""
    _validate_series(history)
    fit, order = _fit_best_order(history)

    try:
        result = fit.get_forecast(steps=horizon)
        mean = np.asarray(result.predicted_mean, dtype=float)
        ci = np.asarray(result.conf_int(alpha=alpha), dtype=float)
        lower, upper = ci[:, 0], ci[:, 1]
    except Exception as e:
        raise ArimaUnavailableError(f"ARIMA fit succeeded but forecasting failed: {e!r}")

    mean = np.clip(mean, 0, None)
    lower = np.clip(lower, 0, None)
    upper = np.clip(np.maximum(upper, mean), 0, None)

    return {"forecast": mean, "lower": lower, "upper": upper, "order": order}


def arima_available(n_history_days: int) -> bool:
    return n_history_days >= MIN_ARIMA_HISTORY_DAYS
