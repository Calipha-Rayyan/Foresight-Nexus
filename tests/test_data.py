import io
import pandas as pd
from data.loader import (
    clean_dataset, validate_columns, data_health_score,
    guess_column, generate_csv_template
)
from core.constants import REQUIRED_COLUMNS, OPTIONAL_COLUMNS


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


def test_clean_dataset_normalizes_promotion_formats():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"],
        "product_id": ["A", "B", "C", "D"],
        "quantity": [10, 20, 30, 40],
        "promotion": ["yes", "0", True, "promo"],
    })
    cleaned, log = clean_dataset(df)
    assert cleaned["promotion"].dtype == bool
    assert cleaned["promotion"].tolist() == [True, False, True, True]
    assert any("promotion" in l for l in log)


def test_clean_dataset_parses_real_world_currency_and_numbers():
    df = pd.DataFrame({
        "date": ["2026-01-01", "2026-01-02"],
        "product_id": ["A", "A"],
        "quantity": ["1,250", "300"],
        "price": ["$14.99", "$25.50"],
        "inventory": ["5,000", "4,700"],
    })
    cleaned, _ = clean_dataset(df)
    assert cleaned["quantity"].sum() == 1550.0
    assert cleaned["price"].iloc[0] == 14.99
    assert cleaned["inventory"].iloc[0] == 5000.0
    assert cleaned["inventory"].iloc[1] == 4700.0


def test_clean_dataset_handles_mixed_date_formats():
    df = pd.DataFrame({
        "date": ["2026-01-15", "2026/01/16", "2026-01-17T08:00:00Z"],
        "product_id": ["A", "B", "C"],
        "quantity": [10, 20, 30],
    })
    cleaned, _ = clean_dataset(df)
    assert len(cleaned) == 3
    assert pd.api.types.is_datetime64_any_dtype(cleaned["date"])


def test_guess_column_exact_and_normalized():
    cols = ["date", "Product_ID", "QUANTITY", "Unit_Price"]
    assert guess_column("date", cols) == "date"
    assert guess_column("product_id", cols) == "Product_ID"
    assert guess_column("quantity", cols) == "QUANTITY"


def test_guess_column_enterprise_aliases():
    cols = [
        "Order Date", "SKU Number", "Item Description", "Units Sold", "Retail Price",
        "Stock on Hand", "Promo Flag", "Product Category", "Supplier Partner", "Lead Time Days"
    ]
    assert guess_column("date", cols) == "Order Date"
    assert guess_column("product_id", cols) == "SKU Number"
    assert guess_column("product_name", cols) == "Item Description"
    assert guess_column("quantity", cols) == "Units Sold"
    assert guess_column("price", cols) == "Retail Price"
    assert guess_column("inventory", cols) == "Stock on Hand"
    assert guess_column("promotion", cols) == "Promo Flag"
    assert guess_column("category", cols) == "Product Category"
    assert guess_column("supplier", cols) == "Supplier Partner"
    assert guess_column("lead_time", cols) == "Lead Time Days"


def test_guess_column_unmatched_returns_none():
    cols = ["unrelated_col_1", "random_notes"]
    assert guess_column("product_id", cols) is None
    assert guess_column("quantity", cols) is None


def test_generate_csv_template():
    csv_text = generate_csv_template()
    assert isinstance(csv_text, str)
    df = pd.read_csv(io.StringIO(csv_text))
    for col in REQUIRED_COLUMNS + OPTIONAL_COLUMNS:
        assert col in df.columns
    assert len(df) >= 3
    assert pd.api.types.is_numeric_dtype(df["quantity"])
    assert pd.api.types.is_numeric_dtype(df["price"])

