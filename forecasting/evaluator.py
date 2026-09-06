"""Time-aware backtesting. Never shuffles observations — always trains on the
past and evaluates on a later, held-out window."""
import numpy as np
import pandas as pd
from forecasting.features import engineer_features, FEATURE_COLUMNS
from forecasting.baseline import naive_forecast, moving_average_forecast, seasonal_naive_forecast
from forecasting.models import get_model
from forecasting.arima import arima_forecast, ArimaUnavailableError
from utils.logging import log_error


def _metrics(actual: np.ndarray, pred: np.ndarray) -> dict:
    actual = np.asarray(actual, dtype=float)
    pred = np.asarray(pred, dtype=float)
    mae = float(np.mean(np.abs(actual - pred)))
    rmse = float(np.sqrt(np.mean((actual - pred) ** 2)))
    denom = np.sum(np.abs(actual))
    wape = float(np.sum(np.abs(actual - pred)) / denom * 100) if denom > 0 else None
    nonzero = actual != 0
    mape = float(np.mean(np.abs((actual[nonzero] - pred[nonzero]) / actual[nonzero])) * 100) if nonzero.sum() else None
    return {"MAE": round(mae, 2), "RMSE": round(rmse, 2),
            "WAPE": round(wape, 2) if wape is not None else None,
            "MAPE": round(mape, 2) if mape is not None else None}


def _fit_predict_ml(train_feat: pd.DataFrame, test_feat: pd.DataFrame, model_name: str):
    train_feat = train_feat.dropna(subset=FEATURE_COLUMNS + ["demand"])
    if len(train_feat) < 20:
        return None
    model = get_model(model_name)
    model.fit(train_feat[FEATURE_COLUMNS], train_feat["demand"])
    test_feat = test_feat.copy()
    test_feat[FEATURE_COLUMNS] = test_feat[FEATURE_COLUMNS].fillna(train_feat[FEATURE_COLUMNS].median())
    preds = model.predict(test_feat[FEATURE_COLUMNS])
    return np.clip(preds, 0, None)


def backtest_models(series: pd.DataFrame, model_names: list, horizon: int = 14, folds: int = 3) -> dict:
    """series: [date, demand] daily. Rolls the train/test split backward `folds`
    times, each time training on everything before a cut point and testing on the
    next `horizon` days. Returns {model_name: metrics}."""
    feat = engineer_features(series)
    n = len(feat)
    results = {name: [] for name in model_names}

    usable_folds = 0
    for fold in range(folds):
        cut = n - horizon * (fold + 1)
        if cut < 30:
            continue
        usable_folds += 1
        train = feat.iloc[:cut]
        test = feat.iloc[cut:cut + horizon]
        if len(test) == 0:
            continue
        actual = test["demand"].values
        train_hist = train["demand"]

        for name in model_names:
            if name == "Naive":
                pred = naive_forecast(train_hist, len(test))
            elif name == "Moving Average":
                pred = moving_average_forecast(train_hist, len(test))
            elif name == "Seasonal Naive":
                pred = seasonal_naive_forecast(train_hist, len(test))
            elif name == "ARIMA":
                try:
                    result = arima_forecast(train_hist, len(test))
                    pred = result["forecast"]
                except ArimaUnavailableError as e:
                    log_error("ARIMA unavailable during backtest fold (product series)", e)
                    continue  # skip this fold for ARIMA; other models still evaluated normally
            else:
                pred = _fit_predict_ml(train, test, name)
                if pred is None:
                    continue
            results[name].append(_metrics(actual, pred))

    summary = {}
    for name, fold_metrics in results.items():
        if not fold_metrics:
            continue
        summary[name] = {
            k: round(float(np.mean([m[k] for m in fold_metrics if m[k] is not None])), 2)
            if any(m[k] is not None for m in fold_metrics) else None
            for k in ["MAE", "RMSE", "WAPE", "MAPE"]
        }
        summary[name]["folds_used"] = usable_folds
    return summary


def select_best_model(summary: dict) -> tuple:
    """Best = lowest WAPE (falls back to MAE if WAPE unavailable)."""
    if not summary:
        return None, "No model could be evaluated — insufficient history."
    def score(item):
        name, m = item
        return m["WAPE"] if m.get("WAPE") is not None else m["MAE"]
    best_name, best_metrics = min(summary.items(), key=score)
    if best_metrics.get("WAPE") is not None:
        reason = (f"Selected because it achieved the lowest weighted average percentage "
                  f"error (WAPE={best_metrics['WAPE']}%) across {best_metrics.get('folds_used')} "
                  f"backtest fold(s) among the models evaluated on this product's history.")
    else:
        reason = (f"Selected because it achieved the lowest mean absolute error "
                  f"(MAE={best_metrics['MAE']}) across {best_metrics.get('folds_used')} backtest "
                  f"fold(s) — WAPE could not be computed because actual demand was zero throughout "
                  f"the backtest window for this product.")
    return best_name, reason
