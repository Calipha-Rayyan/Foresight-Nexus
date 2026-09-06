"""Pure business rules — no explanation text, no orchestration. Each function
answers one yes/no or classification question so it can be tested and reused
independently (by the recommendation engine, Alerts & Risks, and Command
Center's snapshot builder all consult the same rules)."""
from analytics.risk import classify_health, stockout_risk_level, overstock_risk_level


def is_reorder_eligible(current_stock: float, reorder_point: float) -> bool:
    """A product is eligible for reorder once stock falls below its reorder point."""
    return current_stock < reorder_point


def is_fast_mover(avg_daily_demand: float, fleet_median_demand: float, multiplier: float = 1.5) -> bool:
    if fleet_median_demand <= 0:
        return False
    return avg_daily_demand >= fleet_median_demand * multiplier


def is_slow_mover(coverage_days: float, overstock_threshold: int) -> bool:
    return coverage_days == float("inf") or coverage_days >= overstock_threshold


def is_excess_inventory(coverage_days: float, overstock_threshold: int, severity_multiplier: float = 1.5) -> bool:
    return coverage_days != float("inf") and coverage_days >= overstock_threshold * severity_multiplier


def classify_inventory_health(coverage_days: float, stockout_threshold: int, overstock_threshold: int) -> str:
    """Delegates to analytics.risk so health classification has exactly one
    implementation — rules.py is the single call site pages should use."""
    return classify_health(coverage_days, stockout_threshold, overstock_threshold)


def classify_stockout_risk(coverage_days: float, lead_time_days: float) -> str:
    return stockout_risk_level(coverage_days, lead_time_days)


def classify_overstock_risk(coverage_days: float, overstock_threshold: int) -> str:
    return overstock_risk_level(coverage_days, overstock_threshold)


def reorder_threshold_breached(current_stock: float, avg_daily_demand: float, lead_time_days: float) -> bool:
    """Simpler, forecast-free reorder signal used by fast summary pages
    (Command Center, Alerts) where a full safety-stock calculation isn't run
    for every product on every page load."""
    return current_stock < (avg_daily_demand * lead_time_days)
