from enum import Enum


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
