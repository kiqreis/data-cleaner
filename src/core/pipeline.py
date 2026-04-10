import pandas as pd

from src.core.config import PipelineConfig
from src.core.schema import validate_schema
from src.reports.cleaning import CleaningReport
from src.transforms.columns import clean_column_names, strip_str
from src.transforms.deduplicate import drop_duplicates
from src.transforms.dtypes import infer_and_cast_dtypes
from src.transforms.imputation import apply_imputation
from src.transforms.outliers import handle_outliers


def run_pipeline(
    df: pd.DataFrame,
    config: PipelineConfig | None = None,
    learned_imputation: dict | None = None,
) -> tuple[pd.DataFrame, CleaningReport]:
    """Run the full data cleansing pipeline"""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected 'pd.DataFrame', received {type(df).__name__!r}")

    if config is None:
        config = PipelineConfig()

    initial_shape = df.shape
    nulls_before = {c: int(v) for c, v in df.isnull().sum().items() if v > 0}
    duplicates_removed = 0
    inferred: dict[str, str] = {}

    if config.input_schema is not None:
        df = validate_schema(df, config.input_schema)

    if config.normalize_column_names:
        df = clean_column_names(df)

    if config.infer_dtypes:
        df, inferred = infer_and_cast_dtypes(
            df,
            min_numeric_ratio=config.min_numeric_ratio,
            min_datetime_ratio=config.min_datetime_ratio,
            max_category_ratio=config.max_category_ratio,
        )

    if config.str_strip:
        df = strip_str(df)

    if config.drop_duplicates:
        before = len(df)
        df = drop_duplicates(df, subset=config.duplicate_subset)
        duplicates_removed = before - len(df)

    df = apply_imputation(
        df,
        strategy=config.imputation_strategy,
        learned_values=learned_imputation,
        columns=config.imputation_columns,
        fill_value=config.imputation_fill_value,
    )

    df, outliers_count = handle_outliers(
        df,
        method=config.outliers_method,
        strategy=config.outliers_strategy,
        zscore_threshold=config.zscore_threshold,
        iqr_factor=config.iqr_factor,
    )

    df = df.reset_index(drop=True)

    if config.output_schema is not None:
        df = validate_schema(df, config.output_schema)

    report = CleaningReport(
        initial_shape=initial_shape,
        final_shape=df.shape,
        duplicates_removed=duplicates_removed,
        nulls_before=nulls_before,
        nulls_after={c: int(v) for c, v in df.isnull().sum().items() if v > 0},
        outliers_per_column=outliers_count,
        dtypes_inferred=inferred,
    )

    return df, report
