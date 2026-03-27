import argparse

from config import (
    PipelineConfig,
    ImputationStrategy,
    OutlierStrategy,
    OutlierMethod,
)
from pipeline import run_pipeline
from report import build_diagnostic_report
from file_io import load_csv, save_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="data_cleaner — CSV data cleaning pipeline",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--input", required=True, help="Path to input CSV")
    parser.add_argument("--output", required=True, help="Path to output CSV")
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
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = PipelineConfig(
        imputation_strategy=args.imputation,
        outliers_strategy=args.outlier_strategy,
        outliers_method=args.outlier_method,
        drop_duplicates=args.remove_duplicates,
        str_strip=args.trim_strings,
    )

    df = load_csv(args.input)

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

    save_csv(df_clean, args.output)


if __name__ == "__main__":
    main()
