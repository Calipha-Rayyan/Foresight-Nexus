"""Data loading, validation, and cleaning. No silent mutation: every change
made to the user's data is recorded and surfaced back to the UI."""
import pandas as pd
import numpy as np
from core.constants import REQUIRED_COLUMNS


def load_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        return pd.read_csv(uploaded_file)
    elif name.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file)
    raise ValueError("Unsupported file type. Please upload a CSV or XLSX file.")


def validate_columns(df: pd.DataFrame, mapping: dict) -> list:
    """mapping: user-provided {standard_name: actual_column_name}. Returns list of
    missing required columns (empty if valid)."""
    missing = [c for c in REQUIRED_COLUMNS if mapping.get(c) not in df.columns]
    return missing


def apply_mapping(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    inv_map = {v: k for k, v in mapping.items() if v}
    out = df.rename(columns=inv_map)
    return out


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """Returns (cleaned_df, change_log) where change_log is a list of human-readable
    strings describing every modification made."""
    log = []
    df = df.copy()
    n0 = len(df)

    # dates
    if "date" in df.columns:
        before_na = df["date"].isna().sum()
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        invalid_dates = df["date"].isna().sum() - before_na
        if invalid_dates > 0:
            log.append(f"Removed {invalid_dates} rows with unparseable dates.")
        df = df.dropna(subset=["date"])

    # quantity
    if "quantity" in df.columns:
        df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
        bad_qty = df["quantity"].isna().sum()
        if bad_qty > 0:
            log.append(f"Removed {bad_qty} rows with non-numeric quantity.")
        df = df.dropna(subset=["quantity"])
        neg = (df["quantity"] < 0).sum()
        if neg > 0:
            log.append(f"Clipped {neg} rows with negative quantity to 0.")
            df["quantity"] = df["quantity"].clip(lower=0)

    # price / revenue sanity
    if "price" in df.columns:
        df["price"] = pd.to_numeric(df["price"], errors="coerce")
        bad_price = ((df["price"] < 0)).sum()
        if bad_price > 0:
            log.append(f"Set {bad_price} negative price values to missing.")
            df.loc[df["price"] < 0, "price"] = np.nan

    # duplicates
    key_cols = [c for c in ["date", "product_id"] if c in df.columns]
    if key_cols:
        dupes = df.duplicated(subset=key_cols).sum()
        if dupes > 0:
            log.append(f"Aggregated {dupes} duplicate (date, product_id) rows by summing quantity.")
            agg = {"quantity": "sum"}
            for c in df.columns:
                if c not in key_cols and c not in agg:
                    agg[c] = "first"
            df = df.groupby(key_cols, as_index=False).agg(agg)

    removed_total = n0 - len(df)
    if removed_total == 0 and not log:
        log.append("No cleaning required — dataset was already valid.")

    return df.reset_index(drop=True), log


def data_health_score(df: pd.DataFrame, mapping: dict) -> dict:
    total_cells = df.shape[0] * df.shape[1] if df.shape[0] else 1
    missing_pct = df.isna().sum().sum() / total_cells * 100
    key_cols = [c for c in ["date", "product_id"] if c in df.columns]
    dup_pct = (df.duplicated(subset=key_cols).sum() / len(df) * 100) if key_cols and len(df) else 0.0

    score = 100.0
    score -= min(40, missing_pct * 2)
    score -= min(30, dup_pct * 3)
    score = max(0, round(score))

    return {
        "score": int(score),
        "rows": len(df),
        "products": df["product_id"].nunique() if "product_id" in df.columns else 0,
        "date_range": (df["date"].min(), df["date"].max()) if "date" in df.columns and len(df) else (None, None),
        "missing_pct": round(missing_pct, 2),
        "duplicate_pct": round(dup_pct, 2),
    }
