from inventory.formulas import safety_stock, reorder_point, coverage_days, recommended_order_quantity


def test_safety_stock_zero_when_no_variability():
    assert safety_stock(demand_std=0, lead_time_days=7, z=1.65) == 0.0


def test_safety_stock_scales_with_std():
    low = safety_stock(demand_std=2, lead_time_days=7, z=1.65)
    high = safety_stock(demand_std=10, lead_time_days=7, z=1.65)
    assert high > low


def test_reorder_point_includes_safety_stock():
    rp = reorder_point(avg_daily=10, lead_time_days=5, safety_stock_units=20)
    assert rp == 70  # 10*5 + 20


def test_coverage_days_infinite_when_no_demand():
    assert coverage_days(current_inventory=100, avg_daily=0) == float("inf")


def test_coverage_days_basic():
    assert coverage_days(current_inventory=100, avg_daily=10) == 10


def test_recommended_order_quantity_never_negative():
    qty = recommended_order_quantity(current_inventory=1000, reorder_point_units=50, avg_daily=5)
    assert qty == 0
