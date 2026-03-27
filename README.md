# 🧹 Data Cleaner

A modular data cleaning pipeline with both a **Streamlit web UI** and a **CLI interface**.  
Upload any CSV or Excel file, configure the cleaning steps, and download the result instantly.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python)
![Streamlit](https://img.shields.io/badge/Streamlit-latest-red?logo=streamlit)
![Pandas](https://img.shields.io/badge/Pandas-latest-150458?logo=pandas)
![uv](https://img.shields.io/badge/uv-package%20manager-blueviolet)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

- **Column normalization** — strips accents, lowercases and snake_cases all column names
- **Type inference** — automatically detects and converts numeric, datetime and category columns
- **String cleaning** — trims leading/trailing whitespace from text columns
- **Duplicate removal** — drop duplicate rows globally or by a custom column subset
- **Null imputation** — mean, median, mode, zero, forward fill, backward fill or a custom value
- **Outlier handling** — detect via IQR, Z-score or Modified Z-score; remove, clip or flag
- **Schema validation** — optional pre/post pipeline validation with Pandera
- **Diagnostic report** — detailed stats before cleaning
- **Cleaning report** — summary of every change made during the pipeline run
- **Export** — download the cleaned data as CSV or Excel

---

## 📁 Project Structure

```text
data_cleaner/
├── app.py            # Streamlit Web UI
├── main.py           # Entry point
├── pipeline.py       # Central pipeline orchestration
├── config.py         # Enums and PipelineConfig dataclass
├── transform.py      # Column normalization, type inference, deduplication
├── imputation.py     # Missing-value imputation strategies
├── outlier.py        # Outlier detection and treatment
├── report.py         # CleaningReport and DiagnosticReport
├── schema.py         # Pandera schema validation wrapper
├── file_io.py        # File loading and saving helpers
├── pyproject.toml    # Project metadata and dependencies (uv)
├── Dockerfile        # Docker image definition
└── .dockerignore     # Files excluded from Docker build
```

---

## 🚀 Getting Started (uv recommended)

### 1. Install uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Alternative methods:**
```bash
# Homebrew (macOS/Linux)
brew install uv

# WinGet (Windows)
winget install --id=astral-sh.uv -e

# pip (any platform)
pip install uv
```

### 2. Clone and set up the project

```bash
git clone https://github.com/kiqreis/data-cleaner.git
cd data-cleaner
```

### 3. Install dependencies

Managed via `pyproject.toml` and locked in `uv.lock`.

```toml
[project]
name = "data-cleaner"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "streamlit",
    "pandas",
    "numpy",
    "openpyxl",
    "unidecode",
    "pandera",
    "python-dateutil",
]
```

Install with:

```bash
uv sync
```

### 4. Run the app

```bash
uv run streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### 5. Run the CLI

```bash
uv run python main.py --input data/raw.csv --output data/clean.csv
```

---

## 🐳 Running with Docker

No need to install Python or uv locally. Use Docker.

### Build the image

```bash
docker build -t data-cleaner .
```

### Run the container

```bash
docker run -p 8501:8501 data-cleaner
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

### Run with a local data folder mounted (CLI)

```bash
docker run --rm \
  -v $(pwd)/data:/app/data \
  data-cleaner \
  uv run python main.py --input data/raw.csv --output data/clean.csv
```

---

## 🖥️ Web UI — Usage

1. Upload a `.csv` or `.xlsx` file
2. Configure the cleaning options in the sidebar:
   - Toggle column normalization, deduplication, type inference
   - Choose a null imputation strategy
   - Optionally enable outlier detection and choose method + action
3. Click **▶️ Run cleaning**
4. Review results in the **Clean Data** and **Report** tabs
5. Download the cleaned dataset as CSV or Excel

---

## ⌨️ CLI Options

```text
usage: main.py --input INPUT --output OUTPUT [options]

options:
  --input INPUT             Path to input CSV (required)
  --output OUTPUT           Path to output CSV (required)
  --imputation STRATEGY     Null imputation strategy (default: median)
                            choices: drop, mean, median, mode, zero, ffill, bfill, value
  --outlier-strategy ACTION How to handle outliers (default: clip)
                            choices: remove, clip, flag, none
  --outlier-method METHOD   Outlier detection method (default: iqr)
                            choices: iqr, zscore, modified_zscore
  --no-duplicates           Disable duplicate removal
  --no-trim                 Disable string trimming
  --diagnostic              Print a diagnostic report before and after cleaning
  --log-level LEVEL         Logging verbosity (default: INFO)
                            choices: DEBUG, INFO, WARNING, ERROR
```

### Examples

```bash
# Basic cleaning with default settings
uv run python main.py --input raw.csv --output clean.csv

# Median imputation + remove outliers via Z-score
uv run python main.py --input raw.csv --output clean.csv \
  --imputation median --outlier-method zscore --outlier-strategy remove

# Full diagnostic report, debug logging
uv run python main.py --input raw.csv --output clean.csv \
  --diagnostic --no-duplicates --log-level DEBUG
```

---

## ⚙️ Configuration Reference

| Parameter | Type | Default | Description |
|---|---|---|---|
| `normalize_column_names` | `bool` | `True` | Snake_case + remove accents from column names |
| `str_strip` | `bool` | `True` | Strip whitespace from string columns |
| `drop_duplicates` | `bool` | `True` | Remove duplicate rows |
| `duplicate_subset` | `list[str] \| None` | `None` | Columns to consider for deduplication |
| `infer_dtypes` | `bool` | `True` | Auto-convert string columns to numeric/datetime/category |
| `min_numeric_ratio` | `float` | `0.9` | Min proportion of parseable values to convert to numeric |
| `min_datetime_ratio` | `float` | `0.8` | Min proportion to convert to datetime |
| `max_category_ratio` | `float` | `0.05` | Max unique-value ratio to convert to category |
| `imputation_strategy` | `ImputationStrategy` | `MEDIAN` | How to fill null values |
| `imputation_fill_value` | `Any` | `None` | Required when strategy is `VALUE` |
| `imputation_columns` | `list[str] \| None` | `None` | Restrict imputation to specific columns |
| `outliers_method` | `OutlierMethod` | `IQR` | Detection method |
| `outliers_strategy` | `OutlierStrategy` | `CLIP` | Action on detected outliers |
| `zscore_threshold` | `float` | `3.0` | Threshold for Z-score methods |
| `iqr_factor` | `float` | `1.5` | IQR multiplier for bounds calculation |
| `input_schema` | `Any` | `None` | Optional Pandera schema validated before pipeline |
| `output_schema` | `Any` | `None` | Optional Pandera schema validated after pipeline |

---

## 📄 License

This project is licensed under the MIT License.

```text
MIT License

Copyright (c) 2026 Kaique Reis
```