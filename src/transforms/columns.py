import inflection
import pandas as pd
from unidecode import unidecode


def clean_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """Normalize column names: strip whitespace, remove accents, apply snake_case"""
    df = df.copy()
    df.columns = df.columns.map(
        lambda col: inflection.underscore(unidecode(str(col).strip()))
    )
    return df


def strip_str(df: pd.DataFrame) -> pd.DataFrame:
    """Strip leading/trailing whitespace from string columns"""
    df = df.copy()
    str_cols = df.select_dtypes(include=["object"])

    for col in str_cols.columns:
        mask = df[col].notna()
        df.loc[mask, col] = df.loc[mask, col].str.strip()

    return df
