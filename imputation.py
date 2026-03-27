import pandas as pd
import numpy as np
from typing import Any

from config import ImputationStrategy


def fit_imputation(
    df: pd.DataFrame,
    strategy: ImputationStrategy,
    columns: list[str] | None = None,
    fill_value: Any = None,
) -> dict[str, Any]:
    num_columns = (
        df[columns].select_dtypes(include="number").columns
        if columns
        else df.select_dtypes(include="number").columns
    )

    learned: dict[str, Any] = {}

    for column in num_columns:
        series = df[column].dropna()
        if strategy == ImputationStrategy.MEAN:
            learned[column] = series.mean()
        elif strategy == ImputationStrategy.MEDIAN:
            learned[column] = series.median()
        elif strategy == ImputationStrategy.MODE:
            mode = series.mode()
            learned[column] = mode.iloc[0] if not mode.empty else np.nan
        elif strategy == ImputationStrategy.ZERO:
            learned[column] = 0
        elif strategy == ImputationStrategy.VALUE:
            learned[column] = fill_value

    return learned


def apply_imputation(
    df: pd.DataFrame,
    strategy: ImputationStrategy,
    learned_values: dict | None = None,
    columns: list[str] | None = None,
    fill_value: Any = None,
):
    df = df.copy()
    strategy = ImputationStrategy(strategy)

    num_columns = (
        df[columns].select_dtypes(include="number").columns
        if columns
        else df.select_dtypes(include="number").columns
    )

    category_columns = df.select_dtypes(include=["object", "category"]).columns

    if strategy == ImputationStrategy.DROP:
        df = df.dropna()
        return df

    if strategy == ImputationStrategy.FFILL:
        df[num_columns] = df[num_columns].ffill()
    elif strategy == ImputationStrategy.BFILL:
        df[num_columns] = df[num_columns].bfill()
    elif learned_values:
        df[num_columns] = df[num_columns].fillna(value=learned_values)
    else:
        for column in num_columns:
            value = _compute_fill(df[column], strategy, fill_value)
            if value is not None:
                df[column] = df[column].fillna(value)

    for column in category_columns:
        mode = df[column].mode(dropna=True)
        df[column] = df[column].fillna(mode.iloc[0] if not mode.empty else "unknown")

    return df


def _compute_fill(
    series: pd.Series, strategy: ImputationStrategy, fill_value: Any
) -> Any:
    if strategy == ImputationStrategy.MEAN:
        return series.mean()
    if strategy == ImputationStrategy.MEDIAN:
        return series.median()
    if strategy == ImputationStrategy.MODE:
        mode = series.mode(dropna=True)
        return mode.iloc[0] if not mode.empty else None
    if strategy == ImputationStrategy.ZERO:
        return 0
    if strategy == ImputationStrategy.VALUE:
        return fill_value

    return None
