import pandas as pd


def load_csv(path: str, **kwargs) -> pd.DataFrame:
    """Load a CSV file into a DataFrame"""
    return pd.read_csv(path, **kwargs)


def load_excel(path: str, sheet_name: str | int = 0, **kwargs) -> pd.DataFrame:
    """Load an Excel file into a DataFrame"""
    return pd.read_excel(path, sheet_name=sheet_name, **kwargs)


def save_csv(df: pd.DataFrame, path: str, **kwargs) -> None:
    """Save a DataFrame to a CSV file."""
    kwargs.setdefault("index", False)
    df.to_csv(path, **kwargs)


def save_excel(df: pd.DataFrame, path: str, sheet_name: str, **kwargs) -> None:
    """Save a DataFrame to an Excel file"""
    kwargs.setdefault("index", False)
    df.to_excel(path, sheet_name=sheet_name, **kwargs)
