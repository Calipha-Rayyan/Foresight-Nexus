from analytics.risk import classify_health, stockout_risk_level, overstock_risk_level, demand_trend_flag
from analytics.anomalies import detect_anomalies
import pandas as pd
import numpy as np


def test_classify_health_critical_low_coverage():
    assert classify_health(coverage_days=2, stockout_threshold=10, overstock_threshold=60) == "Critical"


def test_classify_health_watch_high_coverage():
    assert classify_health(coverage_days=100, stockout_threshold=10, overstock_threshold=60) == "Watch"


def test_stockout_risk_scales_with_lead_time():
    assert stockout_risk_level(coverage_days=3, lead_time_days=10) == "Critical"
    assert stockout_risk_level(coverage_days=50, lead_time_days=10) == "Low"


def test_demand_trend_flag_spike():
    assert demand_trend_flag(recent_avg=20, prior_avg=10) == "Demand Spike"


def test_demand_trend_flag_decline():
    assert demand_trend_flag(recent_avg=5, prior_avg=10) == "Demand Decline"


def test_demand_trend_flag_none_when_stable():
    assert demand_trend_flag(recent_avg=10.5, prior_avg=10) is None


def test_anomaly_detection_flags_spike():
    dates = pd.date_range("2026-01-01", periods=40)
    demand = [10] * 39 + [200]  # obvious spike on the last day
    series = pd.DataFrame({"date": dates, "demand": demand})
    anomalies = detect_anomalies(series, window=14, z_thresh=2.5)
    assert len(anomalies) >= 1
    assert anomalies.iloc[-1]["anomaly_type"] == "Unusual demand spike detected"
