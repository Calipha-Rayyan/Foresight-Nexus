"""Data loading, validation, and cleaning. No silent mutation: every change
made to the user's data is recorded and surfaced back to the UI."""
import pandas as pd
import numpy as np
from core.constants import REQUIRED_COLUMNS


def load_file(uploaded_file) -> pd.DataFrame:
    name = uploaded_file.name.lower()
    if name.endswith(".csv"):
        try:
            return pd.read_csv(uploaded_file)
        except (UnicodeDecodeError, pd.errors.ParserError):
            if hasattr(uploaded_file, "seek"):
                uploaded_file.seek(0)
            return pd.read_csv(uploaded_file, encoding="latin-1")
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


COLUMN_ALIASES = {
    "date": ["date", "order_date", "transaction_date", "invoice_date", "day", "timestamp", "datetime", "time", "sale_date"],
    "product_id": ["product_id", "sku", "item_id", "item_code", "product_code", "id", "article_id", "part_number", "part_no"],
    "product_name": ["product_name", "product_title", "item_name", "item_description", "description", "title", "name", "product"],
    "quantity": ["quantity", "qty", "units", "units_sold", "volume", "sales_volume", "sales_qty", "amount_sold"],
    "category": ["category", "product_category", "dept", "department", "group", "product_group", "family", "class"],
    "price": ["price", "unit_price", "selling_price", "msrp", "retail_price", "rate", "cost", "unit_cost"],
    "revenue": ["revenue", "sales", "total_sales", "sales_amount", "total_revenue", "turnover", "total_amount", "gross_sales"],
    "promotion": ["promotion", "promo", "is_promo", "is_promotion", "on_promotion", "discount_active", "campaign", "deal"],
    "supplier": ["supplier", "vendor", "manufacturer", "distributor", "brand", "source"],
    "lead_time": ["lead_time", "lead_time_days", "leadtime", "supplier_lead_time", "delivery_days", "procurement_time"],
    "inventory": ["inventory", "stock", "current_stock", "on_hand", "stock_on_hand", "units_in_stock", "qty_on_hand", "physical_stock"],
}


def guess_column(field: str, available_columns: list[str]) -> str | None:
    """Intelligently matches a standard field name to available source columns using aliases."""
    normalized_avail = {c.lower().replace(" ", "").replace("_", "").replace("-", ""): c for c in available_columns}

    # 1. Exact match
    if field in available_columns:
        return field

    # 2. Normalized match
    norm_field = field.lower().replace("_", "").replace(" ", "").replace("-", "")
    if norm_field in normalized_avail:
        return normalized_avail[norm_field]

    # 3. Known aliases exact match
    aliases = COLUMN_ALIASES.get(field, [])
    for alias in aliases:
        norm_alias = alias.lower().replace("_", "").replace(" ", "").replace("-", "")
        if norm_alias in normalized_avail:
            return normalized_avail[norm_alias]

    # 4. Known aliases substring match
    for alias in aliases:
        norm_alias = alias.lower().replace("_", "").replace(" ", "").replace("-", "")
        if len(norm_alias) >= 3:
            for norm_c, orig_c in normalized_avail.items():
                if norm_alias in norm_c:
                    return orig_c

    # 5. Field substring match
    if len(norm_field) >= 3:
        for norm_c, orig_c in normalized_avail.items():
            if norm_field in norm_c or norm_c in norm_field:
                return orig_c

    return None


def generate_csv_template() -> str:
    """Generates a standard, production-ready CSV template for enterprise onboarding."""
    return (
        "date,product_id,product_name,quantity,category,price,revenue,promotion,supplier,lead_time,inventory\n"
        "2026-01-01,SKU-1001,Wireless Ergonomic Mouse,42,Electronics,29.99,1259.58,True,Acme Supply,14,350\n"
        "2026-01-02,SKU-1001,Wireless Ergonomic Mouse,38,Electronics,29.99,1139.62,False,Acme Supply,14,312\n"
        "2026-01-01,SKU-1002,Mechanical USB-C Keyboard,15,Electronics,89.50,1342.50,False,TechLogistics,21,120\n"
        "2026-01-02,SKU-1002,Mechanical USB-C Keyboard,22,Electronics,89.50,1969.00,True,TechLogistics,21,98\n"
    )


def clean_dataset(df: pd.DataFrame) -> tuple[pd.DataFrame, list]:
    """Returns (cleaned_df, change_log) where change_log is a list of human-readable
    strings describing every modification made."""
    log = []
    df = df.copy()
    n0 = len(df)

    # dates
    if "date" in df.columns:
        before_na = df["date"].isna().sum()
        try:
            df["date"] = pd.to_datetime(df["date"], errors="coerce", format="mixed", utc=True).dt.tz_localize(None)
        except Exception:
            df["date"] = pd.to_datetime(df["date"], errors="coerce")
        invalid_dates = df["date"].isna().sum() - before_na
        if invalid_dates > 0:
            log.append(f"Removed {invalid_dates} rows with unparseable dates.")
        df = df.dropna(subset=["date"])

    # quantity
    if "quantity" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["quantity"]):
            df["quantity"] = df["quantity"].astype(str).str.replace(",", "", regex=False).str.strip()
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
    for col in ["price", "revenue"]:
        if col in df.columns:
            if not pd.api.types.is_numeric_dtype(df[col]):
                df[col] = df[col].astype(str).str.replace(r"[^\d.-]", "", regex=True).str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")
            bad_price = (df[col] < 0).sum()
            if bad_price > 0:
                log.append(f"Set {bad_price} negative {col} values to missing.")
                df.loc[df[col] < 0, col] = np.nan

    # inventory
    if "inventory" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["inventory"]):
            df["inventory"] = df["inventory"].astype(str).str.replace(",", "", regex=False).str.strip()
        df["inventory"] = pd.to_numeric(df["inventory"], errors="coerce")
        neg_inv = (df["inventory"] < 0).sum()
        if neg_inv > 0:
            log.append(f"Clipped {neg_inv} rows with negative inventory to 0.")
            df["inventory"] = df["inventory"].clip(lower=0)

    # lead_time
    if "lead_time" in df.columns:
        if not pd.api.types.is_numeric_dtype(df["lead_time"]):
            df["lead_time"] = df["lead_time"].astype(str).str.replace(r"[^\d.]", "", regex=True).str.strip()
        df["lead_time"] = pd.to_numeric(df["lead_time"], errors="coerce")
        bad_lt = (df["lead_time"] < 1).sum()
        if bad_lt > 0:
            log.append(f"Set {bad_lt} lead times < 1 day to default.")
            df.loc[df["lead_time"] < 1, "lead_time"] = np.nan

    # promotion standardization
    if "promotion" in df.columns:
        if not pd.api.types.is_bool_dtype(df["promotion"]):
            if pd.api.types.is_numeric_dtype(df["promotion"]):
                df["promotion"] = df["promotion"].fillna(0).astype(float) > 0
                log.append("Standardized numeric promotion flags into booleans.")
            else:
                s = df["promotion"].astype(str).str.strip().str.lower()
                truthy = {"1", "true", "t", "yes", "y", "promo", "active", "on"}
                df["promotion"] = s.isin(truthy)
                log.append("Standardized string promotion flags into verified booleans.")

    # duplicates
    key_cols = [c for c in ["date", "product_id"] if c in df.columns]
    if key_cols:
        dupes = df.duplicated(subset=key_cols).sum()
        if dupes > 0:
            log.append(f"Aggregated {dupes} duplicate (date, product_id) rows by summing quantity.")
            agg = {"quantity": "sum"}
            for c in df.columns:
                if c not in key_cols and c not in agg:
                    if c == "promotion":
                        agg[c] = "max"
                    elif c in ["price", "inventory"]:
                        agg[c] = "last"
                    else:
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
