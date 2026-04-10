import pandas as pd


def infer_and_cast_dtypes(
    df: pd.DataFrame,
    min_numeric_ratio: float = 0.9,
    min_datetime_ratio: float = 0.8,
    max_category_ratio: float = 0.05,
) -> tuple[pd.DataFrame, dict[str, str]]:
    """Detect and convert columns to numeric, datetime, or category based on content"""
    df = df.copy()
    inferred: dict[str, str] = {}

    for col in df.select_dtypes(include=["object"]).columns:
        series = df[col].dropna()
        if series.empty:
            continue

        numeric = pd.to_numeric(series, errors="coerce")
        if numeric.notna().mean() >= min_numeric_ratio:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            inferred[col] = "numeric"
            continue

        try:
            dt_series = pd.to_datetime(series, errors="coerce")
            if dt_series.notna().mean() >= min_datetime_ratio:
                df[col] = pd.to_datetime(df[col], errors="coerce")
                inferred[col] = "datetime"
                continue
        except Exception:
            pass

        if df[col].nunique() / max(len(df), 1) <= max_category_ratio:
            df[col] = df[col].astype("category")
            inferred[col] = "category"

    return df, inferred


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Force conversion of all columns to numeric, coercing errors to NaN"""
    df = df.copy()
    for col in df.columns:
        converted = pd.to_numeric(df[col], errors="coerce")
        if converted.notna().sum() > 0:
            df[col] = converted
    return df
