import pandas as pd


def drop_duplicates(df: pd.DataFrame, subset: list[str] | None = None) -> pd.DataFrame:
    """Remove duplicate rows limited to a subset of columns"""
    return df.drop_duplicates(subset=subset)
