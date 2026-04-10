from typing import Any

import numpy as np
import pandas as pd

from src.core.enums import ImputationStrategy


def fit_imputation(
    df: pd.DataFrame,
    strategy: ImputationStrategy,
    columns: list[str] | None = None,
    fill_value: Any = None,
) -> dict[str, Any]:
    """Compute fill values for numeric columns based on the chosen strategy"""
    target_cols = (
        df[columns].select_dtypes(include="number").columns
        if columns
        else df.select_dtypes(include="number").columns
    )

    learned: dict[str, Any] = {}

    for col in target_cols:
        series = df[col].dropna()
        if strategy == ImputationStrategy.MEAN:
            learned[col] = series.mean()
        elif strategy == ImputationStrategy.MEDIAN:
            learned[col] = series.median()
        elif strategy == ImputationStrategy.MODE:
            mode = series.mode()
            learned[col] = mode.iloc[0] if not mode.empty else np.nan
        elif strategy == ImputationStrategy.ZERO:
            learned[col] = 0
        elif strategy == ImputationStrategy.VALUE:
            learned[col] = fill_value

    return learned


def apply_imputation(
    df: pd.DataFrame,
    strategy: ImputationStrategy,
    learned_values: dict | None = None,
    columns: list[str] | None = None,
    fill_value: Any = None,
) -> pd.DataFrame:
    """Apply missing value imputation to the DataFrame"""
    df = df.copy()
    strategy = ImputationStrategy(strategy)

    num_cols = (
        df[columns].select_dtypes(include="number").columns
        if columns
        else df.select_dtypes(include="number").columns
    )
    cat_cols = df.select_dtypes(include=["object", "category"]).columns

    if strategy == ImputationStrategy.DROP:
        return df.dropna()

    if strategy == ImputationStrategy.FFILL:
        df[num_cols] = df[num_cols].ffill()
        for col in cat_cols:
            df[col] = df[col].ffill()
    elif strategy == ImputationStrategy.BFILL:
        df[num_cols] = df[num_cols].bfill()
        for col in cat_cols:
            df[col] = df[col].bfill()
    elif learned_values:
        df[num_cols] = df[num_cols].fillna(value=learned_values)
    else:
        for col in num_cols:
            value = _compute_fill(df[col], strategy, fill_value)
            if value is not None:
                df[col] = df[col].fillna(value)

    for col in cat_cols:
        if df[col].isna().any():
            mode = df[col].mode(dropna=True)
            df[col] = df[col].fillna(mode.iloc[0] if not mode.empty else "unknown")

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
