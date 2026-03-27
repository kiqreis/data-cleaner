import pandas as pd
import inflection
from unidecode import unidecode


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = df.columns.map(
        lambda column: inflection.underscore(unidecode(column).strip())
    )

    return df


def strip_str(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    columns = df.select_dtypes(include=["object"])

    if columns.empty:
        return df

    for column in columns:
        df[column] = df[column].astype(str).str.strip()

    return df


def drop_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset)


def infer_and_cast_dtypes(
    df: pd.DataFrame,
    min_numeric_ratio: float = 0.9,
    min_datetime_ratio: float = 0.8,
    max_category_ratio: float = 0.05,
) -> tuple[pd.DataFrame, dict[str, str]]:
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
    for column in df.columns:
        converted = pd.to_numeric(df[column], errors="coerce")
        if converted.notna().sum() > 0:
            df[column] = converted
    return df
