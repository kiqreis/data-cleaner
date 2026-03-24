import pandas as pd
from unidecode import unidecode


def normalize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .map(unidecode)
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )

    return df


def strip_str(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    columns = df.select_dtypes(include="str")

    if columns.empty:
        return df

    for column in columns:
        df[column] = df[column].astype(str).str.strip()

    return df


def drop_duplicates(df: pd.DataFrame, subset=list[str] | None) -> pd.DataFrame:
    return df.drop_duplicates(subset=subset)


def coerce_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    for column in df.columns:
        converted = pd.to_numeric(df[column], errors="coerce")

        if converted.notna().sum() > 0:
            df[column] = converted

    return df
