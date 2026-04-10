import argparse
from pathlib import Path

import pandas as pd

from src.core import (
    ImputationStrategy,
    OutlierMethod,
    OutlierStrategy,
    PipelineConfig,
)
from src.core.pipeline import run_pipeline
from src.io.file_io import load_csv, load_excel, save_csv, save_excel
from src.reports.diagnostic import build_diagnostic_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="data-cleaner — CSV/Excel data cleaning pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--input", required=True, help="Path to input file (CSV or Excel)"
    )
    parser.add_argument(
        "--output", required=True, help="Path to output file (CSV or Excel)"
    )
    parser.add_argument(
        "--imputation",
        default="median",
        choices=[s.value for s in ImputationStrategy],
        help="Null imputation strategy",
    )
    parser.add_argument(
        "--outlier-strategy",
        default="clip",
        choices=[s.value for s in OutlierStrategy],
        dest="outlier_strategy",
        help="How to handle outliers",
    )
    parser.add_argument(
        "--outlier-method",
        default="iqr",
        choices=[m.value for m in OutlierMethod],
        dest="outlier_method",
        help="Outlier detection method",
    )
    parser.add_argument(
        "--no-duplicates",
        action="store_false",
        dest="remove_duplicates",
        help="Disables duplicate removal",
    )
    parser.add_argument(
        "--no-trim",
        action="store_false",
        dest="trim_strings",
        help="Disables string trimming",
    )
    parser.add_argument(
        "--diagnostic",
        action="store_true",
        help="Display diagnostic report before and after",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        dest="log_level",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="data-cleaner 0.1.0",
    )
    return parser.parse_args()


def _load_file(path: str) -> pd.DataFrame:
    """Load a CSV or Excel file based on extension."""
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        return load_csv(path)
    if ext in (".xlsx", ".xls"):
        return load_excel(path)
    raise ValueError(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")


def _save_file(df: pd.DataFrame, path: str) -> None:
    """Save a DataFrame to CSV or Excel based on extension."""
    ext = Path(path).suffix.lower()
    if ext == ".csv":
        save_csv(df, path)
    elif ext in (".xlsx", ".xls"):
        save_excel(df, path)
    else:
        raise ValueError(f"Unsupported file format: {ext}. Use .csv, .xlsx, or .xls")


def main() -> None:
    args = parse_args()

    config = PipelineConfig(
        imputation_strategy=args.imputation,
        outliers_strategy=args.outlier_strategy,
        outliers_method=args.outlier_method,
        drop_duplicates=args.remove_duplicates,
        str_strip=args.trim_strings,
    )

    df = _load_file(args.input)

    if args.diagnostic:
        before = build_diagnostic_report(df)
        print(
            f"\n[BEFORE] shape={before.shape}  nulls={before.total_null_cells}"
            f"  duplicates={before.duplicated_rows}"
        )

    df_clean, report = run_pipeline(df, config)
    print(report.summary())

    if args.diagnostic:
        after = build_diagnostic_report(df_clean)
        print(
            f"[AFTER]  shape={after.shape}  nulls={after.total_null_cells}"
            f"  duplicates={after.duplicated_rows}\n"
        )

    _save_file(df_clean, args.output)
