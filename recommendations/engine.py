"""Per-product recommendation engine. Pure orchestration: combines
inventory formulas + rules.py (eligibility/classification) + explanations.py
(text generation) into one ProductRecommendation. No business rule or
explanation string is written directly in this file — see rules.py and
explanations.py."""
from dataclasses import dataclass
from inventory.formulas import (avg_daily_demand, demand_std_daily, safety_stock,
                                 reorder_point, coverage_days, recommended_order_quantity)
from analytics.risk import days_to_stockout
from recommendations.rules import (is_reorder_eligible, classify_inventory_health,
                                    classify_stockout_risk, classify_overstock_risk)
from recommendations.explanations import demand_trend_note, reorder_explanation, no_reorder_explanation


@dataclass
class ProductRecommendation:
    product_id: str
    product_name: str
    current_stock: float
    avg_daily_demand: float
    forecast_demand_horizon: float
    lead_time_days: float
    safety_stock: float
    reorder_point: float
    recommended_order_qty: float
    coverage_days: float
    days_to_stockout: float
    health: str
    stockout_risk: str
    overstock_risk: str
    should_reorder: bool
    explanation: str


def build_recommendation(product_id: str, product_name: str, recent_demand_series, forecast_df,
                          current_stock: float, lead_time_days: float, settings) -> ProductRecommendation:
    avg_d = avg_daily_demand(recent_demand_series.tail(28))
    std_d = demand_std_daily(recent_demand_series.tail(28))
    ss = safety_stock(std_d, lead_time_days, settings.service_level_z)
    rp = reorder_point(avg_d, lead_time_days, ss)
    cov = coverage_days(current_stock, avg_d)
    dts = days_to_stockout(current_stock, avg_d)
    roq = recommended_order_quantity(current_stock, rp, avg_d)

    health = classify_inventory_health(cov, settings.stockout_risk_days_threshold, settings.overstock_days_threshold)
    s_risk = classify_stockout_risk(cov, lead_time_days)
    o_risk = classify_overstock_risk(cov, settings.overstock_days_threshold)
    should_reorder = is_reorder_eligible(current_stock, rp)

    forecast_horizon_total = (float(forecast_df["forecast"].sum())
                               if forecast_df is not None and len(forecast_df) else avg_d * 30)

    if should_reorder:
        trend_note = ""
        if len(recent_demand_series) >= 56:
            recent28 = recent_demand_series.tail(28).mean()
            prior28 = recent_demand_series.tail(56).head(28).mean()
            trend_note = demand_trend_note(recent28, prior28)
        explanation = reorder_explanation(current_stock, avg_d, lead_time_days, ss, rp, roq, trend_note)
    else:
        explanation = no_reorder_explanation(current_stock, rp)

    return ProductRecommendation(
        product_id=product_id, product_name=product_name, current_stock=current_stock,
        avg_daily_demand=round(avg_d, 2), forecast_demand_horizon=round(forecast_horizon_total, 1),
        lead_time_days=lead_time_days, safety_stock=round(ss, 1), reorder_point=round(rp, 1),
        recommended_order_qty=roq, coverage_days=round(cov, 1) if cov != float("inf") else -1,
        days_to_stockout=round(dts, 1) if dts != float("inf") else -1,
        health=health, stockout_risk=s_risk, overstock_risk=o_risk,
        should_reorder=should_reorder, explanation=explanation,
    )
