import pandas as pd
from recommendations.engine import build_recommendation
from core.config import Settings

SETTINGS = Settings()


def test_recommends_reorder_when_stock_low():
    demand = pd.Series([10] * 60)  # steady 10/day demand
    rec = build_recommendation("P1", "Test Product", demand, None, current_stock=5,
                                lead_time_days=7, settings=SETTINGS)
    assert rec.should_reorder is True
    assert rec.recommended_order_qty > 0
    assert "Recommended order" in rec.explanation


def test_no_reorder_when_stock_ample():
    demand = pd.Series([10] * 60)
    rec = build_recommendation("P1", "Test Product", demand, None, current_stock=5000,
                                lead_time_days=7, settings=SETTINGS)
    assert rec.should_reorder is False
    assert rec.recommended_order_qty == 0
