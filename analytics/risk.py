"""Detects and classifies inventory/demand risk per product using computed
coverage, forecast, and volatility — never hard-coded."""
from core.constants import (HEALTH_HEALTHY, HEALTH_WATCH, HEALTH_AT_RISK, HEALTH_CRITICAL,
                             RISK_CRITICAL, RISK_HIGH, RISK_MEDIUM, RISK_LOW)


def classify_health(coverage_days: float, stockout_threshold: int, overstock_threshold: int) -> str:
    if coverage_days == float("inf"):
        return HEALTH_WATCH  # no demand data — can't assess
    if coverage_days <= stockout_threshold * 0.5:
        return HEALTH_CRITICAL
    if coverage_days <= stockout_threshold:
        return HEALTH_AT_RISK
    if coverage_days >= overstock_threshold:
        return HEALTH_WATCH
    return HEALTH_HEALTHY


def stockout_risk_level(coverage_days: float, lead_time_days: float) -> str:
    if coverage_days == float("inf"):
        return RISK_LOW
    if coverage_days <= lead_time_days * 0.5:
        return RISK_CRITICAL
    if coverage_days <= lead_time_days:
        return RISK_HIGH
    if coverage_days <= lead_time_days * 2:
        return RISK_MEDIUM
    return RISK_LOW


def overstock_risk_level(coverage_days: float, overstock_threshold: int) -> str:
    if coverage_days == float("inf"):
        return RISK_LOW
    if coverage_days >= overstock_threshold * 2:
        return RISK_CRITICAL
    if coverage_days >= overstock_threshold * 1.5:
        return RISK_HIGH
    if coverage_days >= overstock_threshold:
        return RISK_MEDIUM
    return RISK_LOW


def demand_trend_flag(recent_avg: float, prior_avg: float, spike_threshold: float = 0.5,
                       decline_threshold: float = -0.3) -> str | None:
    if prior_avg <= 0:
        return None
    pct_change = (recent_avg - prior_avg) / prior_avg
    if pct_change >= spike_threshold:
        return "Demand Spike"
    if pct_change <= decline_threshold:
        return "Demand Decline"
    return None


def days_to_stockout(current_inventory: float, avg_daily_demand: float) -> float:
    if avg_daily_demand <= 0:
        return float("inf")
    return current_inventory / avg_daily_demand
