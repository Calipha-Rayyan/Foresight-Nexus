import pandas as pd
from utils.formatting import format_units, format_currency, format_pct, format_days
from utils.validation import validate_file_extension, validate_non_empty, validate_date_range
from database.duckdb_manager import load_dataframe, category_totals, product_summary


def test_format_units():
    assert format_units(1234.5) == "1,235" or format_units(1234.5) == "1,234"  # rounding
    assert format_units(None) == "N/A"


def test_format_currency():
    assert format_currency(1000) == "$1,000"
    assert format_currency(None) == "N/A"


def test_format_pct_signed():
    assert format_pct(5, signed=True) == "+5.0%"
    assert format_pct(-5, signed=True) == "-5.0%"


def test_format_days_infinite():
    assert format_days(float("inf")) == "∞"
    assert format_days(10) == "10 days"


def test_validate_file_extension():
    assert validate_file_extension("sales.csv") is True
    assert validate_file_extension("sales.exe") is False


def test_validate_non_empty():
    assert validate_non_empty(pd.DataFrame({"a": [1]})) is True
    assert validate_non_empty(pd.DataFrame()) is False


def test_validate_date_range():
    df = pd.DataFrame({"date": pd.date_range("2026-01-01", periods=30)})
    assert validate_date_range(df, min_days=14) is True
    assert validate_date_range(df, min_days=100) is False


def test_duckdb_category_totals():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=4),
        "product_id": ["A", "A", "B", "B"],
        "product_name": ["Alpha"] * 2 + ["Beta"] * 2,
        "category": ["Cat1", "Cat1", "Cat2", "Cat2"],
        "quantity": [10, 20, 5, 5],
    })
    load_dataframe(df, table_name="test_sales")
    totals = category_totals(table_name="test_sales")
    assert set(totals["category"]) == {"Cat1", "Cat2"}
    cat1_total = totals[totals["category"] == "Cat1"]["total_demand"].iloc[0]
    assert cat1_total == 30


def test_duckdb_product_summary():
    df = pd.DataFrame({
        "date": pd.date_range("2026-01-01", periods=2),
        "product_id": ["A", "A"],
        "product_name": ["Alpha", "Alpha"],
        "quantity": [10, 20],
    })
    load_dataframe(df, table_name="test_sales2")
    summary = product_summary(table_name="test_sales2")
    assert summary.iloc[0]["total_quantity"] == 30
