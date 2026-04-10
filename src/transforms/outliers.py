import numpy as np
import pandas as pd

from src.core.enums import OutlierMethod, OutlierStrategy


def handle_outliers(
    df: pd.DataFrame,
    method: OutlierMethod = OutlierMethod.IQR,
    strategy: OutlierStrategy = OutlierStrategy.CLIP,
    zscore_threshold: float = 3.0,
    iqr_factor: float = 1.5,
) -> tuple[pd.DataFrame, dict[str, int]]:
    """
    Detect and treat outliers in numeric columns.
    Returns the cleaned DataFrame and a dict mapping column names to outlier counts
    """
    method = OutlierMethod(method)
    strategy = OutlierStrategy(strategy)

    if strategy == OutlierStrategy.NONE:
        return df, {}

    df = df.copy()

    num_cols = df.select_dtypes(include="number").columns
    outliers_treated: dict[str, int] = {}
    keep_mask = pd.Series(True, index=df.index)

    for col in num_cols:
        series = df[col].dropna()

        if series.empty:
            outliers_treated[col] = 0
            continue

        lower, upper = _compute_bounds(series, method, iqr_factor, zscore_threshold)

        mask = (df[col] < lower) | (df[col] > upper)
        n_outliers = int(mask.sum())
        outliers_treated[col] = n_outliers

        if n_outliers == 0:
            continue

        if strategy == OutlierStrategy.REMOVE:
            keep_mask &= ~mask
        elif strategy == OutlierStrategy.CLIP:
            df[col] = df[col].clip(lower=lower, upper=upper)
        elif strategy == OutlierStrategy.FLAG:
            df[f"{col}_is_outlier"] = mask.astype(bool)

    if strategy == OutlierStrategy.REMOVE:
        df = df[keep_mask].reset_index(drop=True)

    return df, outliers_treated


def _compute_bounds(
    series: pd.Series,
    method: OutlierMethod,
    iqr_factor: float,
    zscore_threshold: float,
) -> tuple[float, float]:
    if method == OutlierMethod.IQR:
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        return q1 - iqr_factor * iqr, q3 + iqr_factor * iqr

    if method == OutlierMethod.ZSCORE:
        mean, std = series.mean(), series.std()
        d = zscore_threshold * std
        return mean - d, mean + d

    if method == OutlierMethod.MODIFIED:
        median = series.median()
        mad = np.median(np.abs(series - median))
        bound = zscore_threshold * mad / 0.6745
        return median - bound, median + bound

    raise ValueError(f"Unknown outlier method: {method!r}")
