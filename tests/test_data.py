import pandas as pd
from data.loader import clean_dataset, validate_columns, data_health_score


def test_validate_columns_flags_missing():
    df = pd.DataFrame({"date": [], "product_id": []})
    mapping = {"date": "date", "product_id": "product_id", "product_name": None, "quantity": None}
    missing = validate_columns(df, mapping)
    assert "product_name" in missing and "quantity" in missing


def test_clean_dataset_removes_negative_quantity():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "product_id": ["A", "A"],
        "quantity": [-5, 10],
    })
    cleaned, log = clean_dataset(df)
    assert (cleaned["quantity"] >= 0).all()
    assert any("negative quantity" in l for l in log)


def test_clean_dataset_drops_invalid_dates():
    df = pd.DataFrame({
        "date": ["2026-01-01", "not-a-date"],
        "product_id": ["A", "A"],
        "quantity": [5, 5],
    })
    cleaned, log = clean_dataset(df)
    assert len(cleaned) == 1


def test_data_health_score_penalizes_missing_values():
    good = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=10), "product_id": ["A"] * 10, "quantity": range(10)})
    bad = good.copy()
    bad.loc[0:4, "quantity"] = None
    good_health = data_health_score(good, {})
    bad_health = data_health_score(bad, {})
    assert bad_health["score"] < good_health["score"]
