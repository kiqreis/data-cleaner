import pandas as pd
import pandera as pa


def validate_schema(df: pd.DataFrame, schema: pa.DataFrameSchema) -> pd.DataFrame:
    try:
        validated = schema.validate(df)
    except pa.errors.SchemaErrors:
        raise

    return validated
