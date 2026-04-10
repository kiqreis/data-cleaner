from dataclasses import dataclass, field
from typing import Any


@dataclass
class CleaningReport:
    """Summary of all changes made while running a pipeline"""

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
