import pandas as pd


def load_csv(path: str, **kwargs) -> pd.DataFrame:
    return pd.read_csv(path, **kwargs)


def load_excel(path: str, sheet_name: str | int = 0, **kwargs) -> pd.DataFrame:
    return pd.read_excel(path, sheet_name=sheet_name, **kwargs)


def save_csv(df: pd.DataFrame, path: str, **kwargs) -> None:
    kwargs.setdefault("index", False)

    df.to_csv(path, **kwargs)

    return None


def save_excel(df: pd.DataFrame, path: str, sheet_name: str, **kwargs) -> None:
    kwargs.setdefault("index", False)

    df.to_excel(path, sheet_name=sheet_name, **kwargs)

    return None
