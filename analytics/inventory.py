"""Single source of truth for the per-product inventory/risk snapshot.

Before this module existed, Command Center, Inventory Intelligence, Alerts &
Risks, and Recommendations each recomputed similar per-product aggregates
independently — and had drifted (Command Center used the default lead time
for every product's reorder-value estimate, while Alerts/Recommendations
used each product's actual lead time from the data). That meant the same
product could imply different risk on different pages. All pages now call
`build_snapshot()` so `current_stock`, `avg_daily_demand`, `lead_time_days`,
`coverage_days`, and `health` are guaranteed identical everywhere.
"""
import pandas as pd
from analytics.risk import classify_health, stockout_risk_level, overstock_risk_level, days_to_stockout
from inventory.formulas import (coverage_days as _coverage_days, avg_daily_demand as _avg_daily_demand,
                                 demand_std_daily as _demand_std_daily, safety_stock as _safety_stock,
                                 reorder_point as _reorder_point)


def build_snapshot(df: pd.DataFrame, settings) -> pd.DataFrame:
    """Returns one row per product_id with consistent stock/demand/risk fields.
    Reorder eligibility uses the identical safety-stock + reorder-point formula
    as recommendations/engine.py (not a simplified proxy), so the count of
    "products needing reorder" is guaranteed to match between Command Center,
    Alerts & Risks, and the Recommendations page."""
    has_inv = "inventory" in df.columns
    has_price = "price" in df.columns
    has_lead_time = "lead_time" in df.columns

    records = []
    for pid, g in df.groupby("product_id"):
        g = g.sort_values("date")
        tail28 = g["quantity"].tail(28)
        avg_d = _avg_daily_demand(tail28)
        std_d = _demand_std_daily(tail28)
        stock = float(g["inventory"].iloc[-1]) if has_inv else 0.0
        lead_time = (float(g["lead_time"].dropna().iloc[-1])
                     if has_lead_time and g["lead_time"].notna().any()
                     else float(settings.default_lead_time_days))

        ss = _safety_stock(std_d, lead_time, settings.service_level_z)
        rp = _reorder_point(avg_d, lead_time, ss)
        cov = _coverage_days(stock, avg_d)
        dts = days_to_stockout(stock, avg_d)
        health = classify_health(cov, settings.stockout_risk_days_threshold, settings.overstock_days_threshold)
        s_risk = stockout_risk_level(cov, lead_time)
        o_risk = overstock_risk_level(cov, settings.overstock_days_threshold)
        price = float(g["price"].iloc[-1]) if has_price and pd.notna(g["price"].iloc[-1]) else None

        records.append({
            "product_id": pid,
            "product_name": g["product_name"].iloc[0],
            "category": g["category"].iloc[0] if "category" in g.columns else None,
            "avg_daily_demand": avg_d,
            "current_stock": stock,
            "lead_time_days": lead_time,
            "safety_stock": ss,
            "reorder_point": rp,
            "coverage_days": cov if cov != float("inf") else -1,
            "days_to_stockout": dts if dts != float("inf") else -1,
            "health": health,
            "stockout_risk": s_risk,
            "overstock_risk": o_risk,
            "price": price,
            "should_reorder": stock < rp,
        })
    return pd.DataFrame(records)
