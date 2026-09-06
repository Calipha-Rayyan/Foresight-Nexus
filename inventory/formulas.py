"""Transparent, documented inventory formulas.

Assumptions (explicit, not universal truths):
- Demand during lead time is estimated as avg_daily_demand * lead_time_days.
- Safety stock uses the standard demand-variability approach:
      safety_stock = z * demand_std_daily * sqrt(lead_time_days)
  where z is chosen from a target service level (default z=1.65 -> ~95%).
- Reorder point = expected demand during lead time + safety stock.
- Recommended order quantity = target inventory (reorder point + horizon
  coverage) - inventory currently on hand, floored at 0.
- Coverage (days) = current inventory / avg daily demand.
"""
import numpy as np


def avg_daily_demand(daily_demand_series) -> float:
    if len(daily_demand_series) == 0:
        return 0.0
    return float(np.mean(daily_demand_series))


def demand_std_daily(daily_demand_series) -> float:
    if len(daily_demand_series) < 2:
        return 0.0
    return float(np.std(daily_demand_series))


def safety_stock(demand_std: float, lead_time_days: float, z: float) -> float:
    return max(0.0, z * demand_std * np.sqrt(max(lead_time_days, 0)))


def reorder_point(avg_daily: float, lead_time_days: float, safety_stock_units: float) -> float:
    return avg_daily * lead_time_days + safety_stock_units


def coverage_days(current_inventory: float, avg_daily: float) -> float:
    if avg_daily <= 0:
        return float("inf")
    return current_inventory / avg_daily


def recommended_order_quantity(current_inventory: float, reorder_point_units: float,
                                avg_daily: float, target_coverage_days: int = 30) -> float:
    target_inventory = reorder_point_units + avg_daily * target_coverage_days * 0.3
    qty = target_inventory - current_inventory
    return max(0.0, round(qty))
