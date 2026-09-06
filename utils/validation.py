import pandas as pd

MAX_UPLOAD_MB = 200
ALLOWED_EXTENSIONS = {".csv", ".xlsx", ".xls"}


def validate_file_extension(filename: str) -> bool:
    return any(filename.lower().endswith(ext) for ext in ALLOWED_EXTENSIONS)


def validate_non_empty(df: pd.DataFrame) -> bool:
    return df is not None and len(df) > 0


def validate_date_range(df: pd.DataFrame, date_col: str = "date", min_days: int = 14) -> bool:
    if date_col not in df.columns or len(df) == 0:
        return False
    span = (df[date_col].max() - df[date_col].min()).days
    return span >= min_days
