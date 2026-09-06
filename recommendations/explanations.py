"""Generates the plain-language explanation text shown alongside each
recommendation. Pure string formatting — takes already-computed numbers, adds
no business logic of its own, so rules.py/inventory formulas stay the single
source of truth for the numbers themselves."""


def demand_trend_note(recent_avg: float, prior_avg: float) -> str:
    if prior_avg is None or prior_avg <= 0:
        return ""
    pct = (recent_avg - prior_avg) / prior_avg * 100
    return f"Demand changed {pct:+.1f}% over the last 28 days vs. the prior 28. "


def reorder_explanation(current_stock: float, avg_daily_demand: float, lead_time_days: float,
                         safety_stock: float, reorder_point: float, recommended_qty: float,
                         trend_note: str = "") -> str:
    return (
        f"{trend_note}"
        f"Current stock: {current_stock:.0f} units. "
        f"Expected lead-time demand: {avg_daily_demand * lead_time_days:.0f} units "
        f"(avg daily demand {avg_daily_demand:.1f} × {lead_time_days:.0f}-day lead time). "
        f"Safety stock: {safety_stock:.0f} units. "
        f"Projected inventory is below the reorder point of {reorder_point:.0f} units. "
        f"Recommended order: {recommended_qty:.0f} units."
    )


def no_reorder_explanation(current_stock: float, reorder_point: float) -> str:
    return (
        f"Current stock ({current_stock:.0f} units) exceeds the reorder point "
        f"({reorder_point:.0f} units, covering lead-time demand plus safety stock). No reorder needed now."
    )


def forecast_confidence_explanation(confidence_label: str, band_width_pct: float) -> str:
    if confidence_label == "High":
        return f"Forecast confidence is high — the predicted range is tight (±{band_width_pct:.0f}% of the forecast)."
    if confidence_label == "Medium":
        return f"Forecast confidence is medium — recent demand volatility widens the predicted range to ±{band_width_pct:.0f}%."
    return (f"Forecast confidence is low — historical demand for this product is highly volatile, "
            f"widening the predicted range to ±{band_width_pct:.0f}%. Treat this forecast as directional.")


def insufficient_data_explanation(available_days: int, required_days: int) -> str:
    return (f"Insufficient historical data for a reliable forecast at this horizon — "
            f"only {available_days} day(s) of history are available (recommended minimum: {required_days} days). "
            f"A baseline (moving-average) estimate is shown instead of a model-based forecast.")


def overstock_explanation(coverage_days: float, overstock_threshold: int) -> str:
    return (f"Inventory covers {coverage_days:.0f} days of demand — above the "
            f"{overstock_threshold}-day overstock threshold. Consider a promotion or pausing replenishment.")
