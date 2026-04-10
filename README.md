# Data Cleaner

A modular data cleaning pipeline with both a Streamlit web interface and a command-line tool. Upload any CSV or Excel file, configure the cleaning steps, and download the result.

## Features

- **Column normalization**: strips accents, lowercases and snake_cases all column names
- **Type inference**: automatically detects and converts numeric, datetime and category columns
- **String cleaning**: trims leading/trailing whitespace from text columns
- **Duplicate removal**: drop duplicate rows globally or by a custom column subset
- **Null imputation**: mean, median, mode, zero, forward fill, backward fill or a custom value
- **Outlier handling**: detect via IQR, Z-score or Modified Z-score; remove, clip or flag
- **Schema validation**: optional pre/post pipeline validation with Pandera
- **Diagnostic report**: detailed stats before cleaning
- **Cleaning report**: summary of every change made during the pipeline run
- **Export**: download the cleaned data as CSV or Excel

## Project Structure

```text
src/
├── core/
│   ├── config.py         # PipelineConfig dataclass
│   ├── enums.py          # ImputationStrategy, OutlierMethod, OutlierStrategy
│   ├── pipeline.py       # Central orchestration
│   └── schema.py         # Pandera schema validation
├── transforms/
│   ├── columns.py        # Column name normalization, string stripping
│   ├── dtypes.py         # Type inference and casting
│   ├── deduplicate.py    # Duplicate row removal
│   ├── imputation.py     # Missing-value strategies
│   └── outliers.py       # Outlier detection and treatment
├── io/
│   └── file_io.py        # CSV and Excel load/save helpers
├── reports/
│   ├── cleaning.py       # CleaningReport
│   └── diagnostic.py     # DiagnosticReport
└── cli/
    └── main.py           # CLI entry point with argparse

app.py                    # Streamlit web interface
pyproject.toml            # Project metadata and dependencies
Dockerfile                # Container image definition
```

## Getting Started

The project uses [uv](https://docs.astral.sh/uv/) for dependency management. Install it first:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

Clone the repository and install dependencies:

```bash
git clone https://github.com/kiqreis/data-cleaner.git
cd data-cleaner
uv sync
```

### Run the web interface

```bash
uv run streamlit run app.py
```

Then open http://localhost:8501 in your browser.

### Run the CLI

```bash
uv run python -m src --input data/raw.csv --output data/clean.csv
```

The CLI accepts both CSV and Excel files for input and output, it detects the format from the file extension.

## Using Docker

Build the image:

```bash
docker build -t data-cleaner .
```

Run the web interface:

```bash
docker run -p 8501:8501 data-cleaner
```

Run the CLI with a local data directory mounted:

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  data-cleaner \
  uv run python -m src --input data/raw.csv --output data/clean.csv
```

## How It Works

The pipeline applies a series of transformations in order:

1. **Schema validation**: optional Pandera check before cleaning
2. **Column normalization**: snake_case and accent removal
3. **Type inference**: detects numeric, datetime and category columns
4. **String stripping**: trims whitespace from text columns
5. **Deduplication**: removes duplicate rows
6. **Null imputation**: fills missing values using the chosen strategy
7. **Outlier handling**: detects and treats outliers
8. **Schema validation**: optional Pandera check after cleaning

Each step can be toggled on or off through the `PipelineConfig` dataclass, either programmatically or via the CLI flags.

## CLI Options

```
usage: python -m src --input INPUT --output OUTPUT [options]

options:
  --input INPUT             Path to input file (CSV or Excel)
  --output OUTPUT           Path to output file (CSV or Excel)
  --imputation STRATEGY     Null imputation (default: median)
                            choices: drop, mean, median, mode, zero, ffill, bfill, value
  --outlier-strategy ACTION Outlier handling (default: clip)
                            choices: remove, clip, flag, none
  --outlier-method METHOD   Outlier detection (default: iqr)
                            choices: iqr, zscore, modified_zscore
  --no-duplicates           Disable duplicate removal
  --no-trim                 Disable string trimming
  --diagnostic              Print a diagnostic report before and after
  --log-level LEVEL         Logging verbosity (default: INFO)
  --version                 Show version and exit
```

### Examples

Basic cleaning with default settings:

```bash
uv run python -m src --input raw.csv --output clean.csv
```

Median imputation with Z-score outlier removal:

```bash
uv run python -m src --input raw.csv --output clean.csv \
  --imputation median --outlier-method zscore --outlier-strategy remove
```

Full diagnostic report with debug logging:

```bash
uv run python -m src --input raw.csv --output clean.csv \
  --diagnostic --no-duplicates --log-level DEBUG
```

## Using as a Library

The project can also be imported as a Python library:

```python
from src import PipelineConfig, run_pipeline, load_csv

df = load_csv("data/raw.csv")
config = PipelineConfig(imputation_strategy="median", drop_duplicates=True)
df_clean, report = run_pipeline(df, config)
print(report.summary())
```

## License

MIT License

Copyright (c) 2026 Kaique Reis
