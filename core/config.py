"""FORESIGHT Nexus - global configuration."""
from dataclasses import dataclass

APP_NAME = "FORESIGHT Nexus"
APP_TAGLINE = "See demand before it happens."
APP_CATEGORY = "AI Demand & Inventory Intelligence Platform"


@dataclass
class Settings:
    forecast_horizon_days: int = 30
    default_lead_time_days: int = 7
    service_level_z: float = 1.65  # ~95% service level
    stockout_risk_days_threshold: int = 10
    overstock_days_threshold: int = 60
    min_history_days_for_ml: int = 90
    backtest_folds: int = 3
    backtest_horizon_days: int = 14


DEFAULT_SETTINGS = Settings()
