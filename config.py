from dataclasses import dataclass
from enum import Enum
from typing import Any


class ImputationStrategy(str, Enum):
    DROP = "drop"
    MEAN = "mean"
    MEDIAN = "median"
    MODE = "mode"
    ZERO = "zero"
    FFILL = "ffill"
    BFILL = "bfill"
    VALUE = "value"


class OutlierStrategy(str, Enum):
    REMOVE = "remove"
    CLIP = "clip"
    FLAG = "flag"
    NONE = "none"


class OutlierMethod(str, Enum):
    IQR = "iqr"
    ZSCORE = "zscore"
    MODIFIED = "modified_zscore"


@dataclass
class PipelineConfig:
    normalize_column_names: bool = True
    str_strip: bool = True
    drop_duplicates: bool = True
    duplicate_subset: list[str] | None = None
    infer_dtypes: bool = True
    min_numeric_ratio: float = 0.9
    min_datetime_ratio: float = 0.8
    max_category_ratio: float = 0.05
    imputation_strategy: ImputationStrategy | str = ImputationStrategy.MEDIAN
    imputation_fill_value: Any = None
    imputation_columns: list[str] | None = None
    outliers_method: OutlierMethod | str = OutlierMethod.IQR
    outliers_strategy: OutlierStrategy | str = OutlierStrategy.CLIP
    zscore_threshold: float = 3.0
    iqr_factor: float = 1.5
    schema: Any = None

    def __post_init__(self) -> None:
        self.imputation_strategy = ImputationStrategy(self.imputation_strategy)
        self.outliers_method = OutlierMethod(self.outliers_method)
        self.outliers_strategy = OutlierStrategy(self.outliers_strategy)

        self._validate()

    def _validate(self) -> None:
        if (
            self.imputation_strategy == ImputationStrategy.VALUE
            and self.imputation_fill_value is None
        ):
            raise ValueError("Provide fill value when imputation strategy is value")

        for name, value in (
            ("min_numeric_ratio", self.min_numeric_ratio),
            ("min_datetime_ratio", self.min_datetime_ratio),
            ("max_category_ratio", self.max_category_ratio),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0.0 and 1.0")
        if self.zscore_threshold <= 0:
            raise ValueError("zscore_threshold must be positive")
        if self.iqr_factor <= 0:
            raise ValueError("iqr_factor must be positive")
