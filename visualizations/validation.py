"""Data validation and safe-formatting helpers for FORESIGHT Nexus visualizations.

Guarantees zero `undefined`, `null`, `None`, `NaN`, or `NaT` strings appear in
chart titles, axis labels, hover templates, legends, or metric displays.
"""
from typing import Any, Union
import numpy as np
import pandas as pd


def safe_label(val: Any, default: str = "—") -> str:
    """Sanitizes any string, object, or category value.
    Replaces None, NaN, empty strings, and literal 'undefined'/'null'/'none'
    with a meaningful fallback.
    """
    if val is None:
        return default
    if isinstance(val, (float, np.floating)) and np.isnan(val):
        return default
    if pd.isna(val):
        return default
    s = str(val).strip()
    if not s or s.lower() in ("none", "nan", "nat", "null", "undefined", "n/a"):
        return default
    return s


def safe_product_name(val: Any, default: str = "All Products") -> str:
    """Sanitizes product names for titles and hover templates."""
    cleaned = safe_label(val, default=default)
    return default if cleaned == "—" else cleaned


def safe_category(val: Any, default: str = "Unassigned") -> str:
    """Sanitizes category labels."""
    cleaned = safe_label(val, default=default)
    return default if cleaned == "—" else cleaned


def safe_numeric(val: Any, default: float = 0.0, decimals: int | None = None) -> Union[int, float]:
    """Safely converts input to a finite numeric value. Never returns NaN or None."""
    if val is None:
        return default
    try:
        f = float(val)
        if not np.isfinite(f) or np.isnan(f):
            return default
        if decimals is not None:
            return round(f, decimals)
        return f
    except (ValueError, TypeError):
        return default


def safe_date(val: Any, default: str = "—", fmt: str = "%b %d, %Y") -> str:
    """Formats date objects safely without NaT or None output."""
    if val is None or pd.isna(val):
        return default
    try:
        ts = pd.to_datetime(val)
        if pd.isna(ts):
            return default
        return ts.strftime(fmt)
    except Exception:
        return default


def validate_chart_df(df: pd.DataFrame | None, required_cols: list[str]) -> pd.DataFrame:
    """Ensures df is a valid DataFrame containing all required columns,
    dropping rows where critical coordinates are null, returning an empty
    valid DataFrame with correct columns if input is None or empty.
    """
    if df is None or not isinstance(df, pd.DataFrame) or df.empty:
        return pd.DataFrame(columns=required_cols)
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        res = df.copy()
        for c in missing:
            res[c] = np.nan
        return res
    return df.dropna(subset=[c for c in required_cols if c in df.columns])
