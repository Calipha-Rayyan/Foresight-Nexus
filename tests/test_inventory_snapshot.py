import pandas as pd
from analytics.inventory import build_snapshot
from core.config import Settings

SETTINGS = Settings()


def _make_df():
    dates = pd.date_range("2026-01-01", periods=60)
    rows = []
    for d in dates:
        rows.append({"date": d, "product_id": "P1", "product_name": "Widget", "category": "Cat",
                     "quantity": 10, "price": 5.0, "lead_time": 7, "inventory": 20})
    return pd.DataFrame(rows)


def test_snapshot_has_one_row_per_product():
    df = _make_df()
    snap = build_snapshot(df, SETTINGS)
    assert len(snap) == 1
    assert snap.iloc[0]["product_id"] == "P1"


def test_snapshot_current_stock_matches_latest_inventory_row():
    df = _make_df()
    df.loc[df.index[-1], "inventory"] = 999  # last row should win
    snap = build_snapshot(df, SETTINGS)
    assert snap.iloc[0]["current_stock"] == 999


def test_snapshot_uses_product_lead_time_not_default():
    df = _make_df()
    df["lead_time"] = 14  # not the default (7)
    snap = build_snapshot(df, SETTINGS)
    assert snap.iloc[0]["lead_time_days"] == 14


def test_snapshot_falls_back_to_default_lead_time_when_missing():
    df = _make_df().drop(columns=["lead_time"])
    snap = build_snapshot(df, SETTINGS)
    assert snap.iloc[0]["lead_time_days"] == SETTINGS.default_lead_time_days


def test_snapshot_should_reorder_matches_reorder_point_not_simple_threshold():
    # Steady demand=10/day, lead_time=7 -> simple threshold would be 70.
    # With safety stock (std=0 here since demand is constant), reorder_point == 70 too,
    # so stock=65 should be flagged for reorder under both — verifies no crash/mismatch.
    df = _make_df()
    df["inventory"] = 65
    snap = build_snapshot(df, SETTINGS)
    assert bool(snap.iloc[0]["should_reorder"]) is True


def test_snapshot_no_price_column_yields_none_price():
    df = _make_df().drop(columns=["price"])
    snap = build_snapshot(df, SETTINGS)
    assert snap.iloc[0]["price"] is None
