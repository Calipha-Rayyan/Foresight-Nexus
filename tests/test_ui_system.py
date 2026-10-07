"""Tests for FORESIGHT Nexus UI system, data sanitization, and visualization safety."""
import pandas as pd
import numpy as np
from pathlib import Path
from visualizations.validation import (
    safe_label,
    safe_product_name,
    safe_category,
    safe_numeric,
    safe_date,
    validate_chart_df,
)
from visualizations.forecast_charts import create_demand_forecast_chart
from visualizations.risk_charts import create_anomaly_timeline_chart
from ui.branding import get_svg_data_uri, get_favicon, MARK_FILE, LOGO_FILE
from ui.status import render_status_badge


def test_safe_label_sanitizes_bad_values():
    assert safe_label(None) == "—"
    assert safe_label(np.nan) == "—"
    assert safe_label("undefined") == "—"
    assert safe_label("null") == "—"
    assert safe_label("NaN") == "—"
    assert safe_label("NaT") == "—"
    assert safe_label("Valid Label") == "Valid Label"


def test_safe_product_name_fallback():
    assert safe_product_name(None) == "All Products"
    assert safe_product_name("undefined") == "All Products"
    assert safe_product_name("Wireless Mouse") == "Wireless Mouse"


def test_safe_numeric_converts_and_handles_nan():
    assert safe_numeric(None, default=0.0) == 0.0
    assert safe_numeric(np.nan, default=0.0) == 0.0
    assert safe_numeric(float("inf"), default=0.0) == 0.0
    assert safe_numeric("42.5", decimals=1) == 42.5
    assert safe_numeric(12.3456, decimals=2) == 12.35


def test_safe_date_formatting():
    assert safe_date(None) == "—"
    assert safe_date(pd.NaT) == "—"
    ts = pd.Timestamp("2026-05-15")
    assert "May 15, 2026" in safe_date(ts)


def test_validate_chart_df_handles_missing_columns():
    df = pd.DataFrame({"date": [1, 2], "demand": [10, 20]})
    validated = validate_chart_df(df, ["date", "demand"])
    assert len(validated) == 2

    empty_validated = validate_chart_df(None, ["date", "demand"])
    assert list(empty_validated.columns) == ["date", "demand"]


def test_brand_assets_exist_and_encode_as_data_uris():
    mark_uri = get_svg_data_uri(MARK_FILE)
    assert mark_uri is not None
    assert mark_uri.startswith("data:image/svg+xml;base64,")

    logo_uri = get_svg_data_uri(LOGO_FILE)
    assert logo_uri is not None
    assert logo_uri.startswith("data:image/svg+xml;base64,")

    favicon_path = get_favicon()
    assert Path(favicon_path).exists()


def test_status_badge_html_rendering():
    badge = render_status_badge("Critical")
    assert "fn-pill-critical" in badge
    assert "Critical" in badge

    healthy = render_status_badge("Healthy")
    assert "fn-pill-healthy" in healthy


def test_forecast_chart_does_not_use_unified_hover():
    dates = pd.date_range("2026-01-01", periods=30)
    history = pd.DataFrame({"date": dates, "demand": [20] * 30})
    fc_dates = pd.date_range("2026-01-31", periods=14)
    forecast_df = pd.DataFrame({"date": fc_dates, "forecast": [22] * 14, "lower": [18] * 14, "upper": [26] * 14})

    fig = create_demand_forecast_chart(history, forecast_df, product_name="Test SKU")
    # Must NOT use "x unified" which creates Plotly 'undefined' values
    assert fig.layout.hovermode != "x unified"
    assert "Test SKU" in fig.layout.title.text


def test_anomaly_chart_does_not_use_unified_hover():
    dates = pd.date_range("2026-01-01", periods=20)
    series = pd.DataFrame({"date": dates, "demand": [10] * 20})
    anomalies = pd.DataFrame({"date": [dates[5]], "demand": [150]})

    fig = create_anomaly_timeline_chart(series, anomalies)
    assert fig.layout.hovermode != "x unified"


def test_forecast_accuracy_chart_handles_architecture_and_model_columns():
    from visualizations.forecast_charts import create_forecast_accuracy_chart
    # Test with "Architecture" column
    df_arch = pd.DataFrame({
        "Architecture": ["ARIMA", "Random Forest"],
        "WAPE (%)": [12.5, 18.2]
    })
    fig_arch = create_forecast_accuracy_chart(df_arch)
    assert fig_arch is not None
    assert len(fig_arch.data) == 1

    # Test with "Model" column
    df_model = pd.DataFrame({
        "Model": ["ARIMA", "Linear Regression"],
        "WAPE (%)": [11.0, 21.4]
    })
    fig_model = create_forecast_accuracy_chart(df_model)
    assert fig_model is not None
    assert len(fig_model.data) == 1


def test_stockout_risk_chart_handles_zero_days():
    from visualizations.inventory_charts import create_stockout_risk_chart
    snap = pd.DataFrame({
        "product_name": ["Critical Item", "Healthy Item"],
        "days_to_stockout": [0.0, 15.0]
    })
    fig = create_stockout_risk_chart(snap)
    assert fig is not None
    assert fig.layout.xaxis.rangemode == "nonnegative"


def test_render_nexus_visual_markup():
    from ui.three_d import render_nexus_visual
    # Should execute without errors
    render_nexus_visual(height=180)


def test_build_table_column_config_promotion_active():
    from ui.tables import build_table_column_config
    df = pd.DataFrame({"product_id": ["P1"], "promotion": [True]})
    cfg = build_table_column_config(df, editable_columns=["promotion"])
    assert "promotion" in cfg
    promo_col = cfg["promotion"]
    # CheckboxColumn is active / enabled
    assert promo_col.get("disabled") is False or promo_col.get("disabled") is None
    assert "Promotion" in promo_col.get("label", "")


def test_build_table_column_config_monetary_and_dates():
    from ui.tables import build_table_column_config
    df = pd.DataFrame({
        "date": ["2026-01-01"],
        "price": [19.99],
        "revenue": [599.70],
        "quantity": [30],
        "inventory": [150],
        "promotion": [False],
    })
    cfg = build_table_column_config(df)
    assert "date" in cfg
    assert "price" in cfg
    assert "revenue" in cfg
    assert "quantity" in cfg
    assert "inventory" in cfg
    assert "promotion" in cfg

