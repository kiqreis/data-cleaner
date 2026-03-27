from dataclasses import dataclass, field
from typing import Any

import pandas as pd


@dataclass
class CleaningReport:
    initial_shape: tuple[int, int] = (0, 0)
    final_shape: tuple[int, int] = (0, 0)
    duplicates_removed: int = 0
    nulls_before: dict[str, int] = field(default_factory=dict)
    nulls_after: dict[str, int] = field(default_factory=dict)
    outliers_per_column: dict[str, int] = field(default_factory=dict)
    dtypes_inferred: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        rows_removed = self.initial_shape[0] - self.final_shape[0]
        return {
            "shape": {
                "before": self.initial_shape,
                "after": self.final_shape,
                "rows_removed": rows_removed,
            },
            "duplicates_removed": self.duplicates_removed,
            "nulls": {
                "before": sum(self.nulls_before.values()),
                "after": sum(self.nulls_after.values()),
                "by_column_before": self.nulls_before,
                "by_column_after": self.nulls_after,
            },
            "outliers": {
                "total": sum(self.outliers_per_column.values()),
                "by_column": self.outliers_per_column,
            },
            "dtypes_inferred": self.dtypes_inferred,
        }

    def summary(self) -> dict[str, Any]:
        return self.to_dict()


@dataclass
class DiagnosticReport:
    shape: tuple[int, int]
    duplicated_rows: int
    duplicated_pct: float
    null_count: dict[str, int]
    null_pct: dict[str, float]
    total_null_cells: int
    unique_values: dict[str, int]
    constant_columns: list[str]
    dtypes: dict[str, str]
    blank_strings: dict[str, int]
    numeric_summary: dict[str, Any]
    skewness: dict[str, float]
    kurtosis: dict[str, float]
    outliers_iqr: dict[str, int]
    outliers_zscore: dict[str, int]

    def to_dict(self) -> dict[str, Any]:
        return {
            "shape": self.shape,
            "duplicates": {
                "count": self.duplicated_rows,
                "pct": self.duplicated_pct,
            },
            "nulls": {
                "total_cells": self.total_null_cells,
                "by_column": self.null_count,
                "pct_by_column": self.null_pct,
            },
            "cardinality": {
                "unique_values": self.unique_values,
                "constant_columns": self.constant_columns,
            },
            "dtypes": self.dtypes,
            "blank_strings": self.blank_strings,
            "numeric": {
                "summary": self.numeric_summary,
                "skewness": self.skewness,
                "kurtosis": self.kurtosis,
            },
            "outliers": {
                "iqr": self.outliers_iqr,
                "zscore": self.outliers_zscore,
            },
        }

    def summary(self) -> dict[str, Any]:
        return self.to_dict()


def build_diagnostic_report(df: pd.DataFrame) -> DiagnosticReport:
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected pd.DataFrame, received {type(df).__name__!r}")

    num_df = df.select_dtypes(include="number")
    obj_cols = df.select_dtypes(include="object").columns
    dup = df.duplicated()

    outliers_iqr: dict[str, int] = {}
    outliers_zscore: dict[str, int] = {}

    for col in num_df.columns:
        series = num_df[col].dropna()
        q1, q3 = series.quantile(0.25), series.quantile(0.75)
        iqr = q3 - q1
        outliers_iqr[col] = int(
            ((num_df[col] < q1 - 1.5 * iqr) | (num_df[col] > q3 + 1.5 * iqr)).sum()
        )
        std = series.std()
        if std > 0:
            z = (num_df[col] - series.mean()) / std
            outliers_zscore[col] = int((z.abs() > 3).sum())
        else:
            outliers_zscore[col] = 0

    blank_strings = {
        col: int(df[col].dropna().str.strip().eq("").sum()) for col in obj_cols
    }

    return DiagnosticReport(
        shape=df.shape,
        duplicated_rows=int(dup.sum()),
        duplicated_pct=round(float(dup.mean()) * 100, 2),
        null_count=df.isnull().sum().to_dict(),
        null_pct=(df.isnull().mean() * 100).round(2).to_dict(),
        total_null_cells=int(df.isnull().sum().sum()),
        unique_values=df.nunique().to_dict(),
        constant_columns=[c for c in df.columns if df[c].nunique(dropna=False) <= 1],
        dtypes=df.dtypes.astype(str).to_dict(),
        blank_strings=blank_strings,
        numeric_summary=(
            num_df.describe().round(4).to_dict() if not num_df.empty else {}
        ),
        skewness=num_df.skew().round(4).to_dict(),
        kurtosis=num_df.kurtosis().round(4).to_dict(),
        outliers_iqr=outliers_iqr,
        outliers_zscore=outliers_zscore,
    )
