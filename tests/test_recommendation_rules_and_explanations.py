from recommendations.rules import (is_reorder_eligible, is_fast_mover, is_slow_mover, is_excess_inventory,
                                    classify_inventory_health, classify_stockout_risk, classify_overstock_risk,
                                    reorder_threshold_breached)
from recommendations.explanations import (demand_trend_note, reorder_explanation, no_reorder_explanation,
                                           forecast_confidence_explanation, insufficient_data_explanation,
                                           overstock_explanation)


def test_is_reorder_eligible():
    assert is_reorder_eligible(current_stock=10, reorder_point=50) is True
    assert is_reorder_eligible(current_stock=100, reorder_point=50) is False


def test_is_fast_mover():
    assert is_fast_mover(avg_daily_demand=30, fleet_median_demand=10) is True
    assert is_fast_mover(avg_daily_demand=10, fleet_median_demand=10) is False
    assert is_fast_mover(avg_daily_demand=10, fleet_median_demand=0) is False


def test_is_slow_mover():
    assert is_slow_mover(coverage_days=float("inf"), overstock_threshold=60) is True
    assert is_slow_mover(coverage_days=90, overstock_threshold=60) is True
    assert is_slow_mover(coverage_days=20, overstock_threshold=60) is False


def test_is_excess_inventory():
    assert is_excess_inventory(coverage_days=100, overstock_threshold=60) is True
    assert is_excess_inventory(coverage_days=70, overstock_threshold=60) is False


def test_classify_functions_delegate_correctly():
    assert classify_inventory_health(2, 10, 60) == "Critical"
    assert classify_stockout_risk(3, 10) == "Critical"
    assert classify_overstock_risk(150, 60) == "Critical"


def test_reorder_threshold_breached():
    assert reorder_threshold_breached(current_stock=10, avg_daily_demand=5, lead_time_days=7) is True
    assert reorder_threshold_breached(current_stock=100, avg_daily_demand=5, lead_time_days=7) is False


def test_demand_trend_note_empty_when_no_prior():
    assert demand_trend_note(10, None) == ""
    assert demand_trend_note(10, 0) == ""


def test_demand_trend_note_formats_percentage():
    note = demand_trend_note(recent_avg=15, prior_avg=10)
    assert "+50.0%" in note


def test_reorder_explanation_contains_key_numbers():
    text = reorder_explanation(current_stock=10, avg_daily_demand=5, lead_time_days=7,
                                safety_stock=8, reorder_point=43, recommended_qty=50)
    assert "10 units" in text
    assert "Recommended order:\n50 units.".split("\n")[-1] in text or "50 units" in text


def test_no_reorder_explanation():
    text = no_reorder_explanation(current_stock=500, reorder_point=50)
    assert "500" in text and "50" in text


def test_forecast_confidence_explanation_varies_by_label():
    high = forecast_confidence_explanation("High", 10)
    low = forecast_confidence_explanation("Low", 60)
    assert "high" in high.lower()
    assert "low" in low.lower()


def test_insufficient_data_explanation_mentions_days():
    text = insufficient_data_explanation(available_days=10, required_days=90)
    assert "10" in text and "90" in text


def test_overstock_explanation_mentions_threshold():
    text = overstock_explanation(coverage_days=120, overstock_threshold=60)
    assert "120" in text and "60" in text
