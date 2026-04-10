import io

import pandas as pd
import streamlit as st

from src.core import ImputationStrategy, OutlierMethod, OutlierStrategy, PipelineConfig
from src.core.pipeline import run_pipeline

st.set_page_config(
    page_title="Spreadsheet Cleaner",
    layout="wide",
    page_icon="🧹",
)

st.title(":material/mop: Spreadsheet Cleaner")

file = st.file_uploader("Upload file (CSV or Excel)", type=["csv", "xlsx"])

if not file:
    st.info("Upload a CSV or Excel file to get started", icon=":material/upload_file:")
    st.stop()


@st.cache_data(show_spinner="Loading file...")
def load_file(data: bytes, name: str) -> pd.DataFrame:
    buffer = io.BytesIO(data)
    return pd.read_csv(buffer) if name.endswith(".csv") else pd.read_excel(buffer)


df_raw = load_file(file.read(), file.name)


with st.sidebar:
    st.header(":material/settings: Pipeline settings")
    st.subheader(":material/table: Columns and strings")

    normalize_cols = st.checkbox("Normalize column names", value=True)
    strip_str = st.checkbox("Strip extra whitespace from strings", value=True)
    do_duplicates = st.checkbox("Remove duplicates", value=True)
    infer_dtypes = st.checkbox("Infer and convert types", value=True)

    subset_cols: list[str] | None = None

    if do_duplicates:
        options = ["[all columns]", *list(df_raw.columns)]
        chosen = st.multiselect("Duplicate subset", options, default=["[all columns]"])

        if "[all columns]" not in chosen and chosen:
            subset_cols = chosen

    st.divider()

    st.subheader(":material/healing: Missing Values")

    imputation = st.selectbox(
        "Imputation strategy",
        options=[s.value for s in ImputationStrategy],
        format_func=lambda x: {
            "drop": "❌ Drop rows",
            "mean": "📊 Mean (numeric)",
            "median": "📊 Median (numeric)",
            "mode": "📊 Mode",
            "zero": "0️⃣  Replace with zero",
            "ffill": "⬆️ Forward fill",
            "bfill": "⬇️ Backward fill",
            "value": "✏️ Custom value",
        }[x],
        index=2,
    )

    fill_value = None

    if imputation == "value":
        fill_value = st.text_input("Replacement value")

    st.divider()
    st.subheader(":material/troubleshoot: Outliers")

    handle_outliers = st.checkbox("Detect and handle outliers", value=False)

    outlier_method = OutlierMethod.IQR.value
    outlier_strategy = OutlierStrategy.NONE.value
    iqr_factor = 1.5
    zscore_thresh = 3.0

    if handle_outliers:
        outlier_method = st.selectbox(
            "Detection method",
            options=[m.value for m in OutlierMethod],
            format_func=lambda x: {
                "iqr": "📦 IQR (Interquartile Range)",
                "zscore": "📈 Z-Score",
                "modified_zscore": "🛡️ Modified Z-score (MAD)",
            }[x],
        )

        outlier_strategy = st.selectbox(
            "Outlier action",
            options=[s.value for s in OutlierStrategy if s != OutlierStrategy.NONE],
            format_func=lambda x: {
                "remove": "🗑️ Remove rows",
                "clip": "✂️ Clip to bounds",
                "flag": "🚩 Flag (new column)",
            }[x],
        )

        if outlier_method == "iqr":
            iqr_factor = st.slider("IQR Factor", 1.0, 3.0, 1.5, 0.1)
        else:
            zscore_thresh = st.slider("Z-score Threshold", 2.0, 5.0, 3.0, 0.5)

    st.divider()

    run_btn = st.button(
        "Run cleaning", width="stretch", type="primary", icon=":material/play_arrow:"
    )


@st.cache_data(show_spinner="Cleaning data...")
def execute_pipeline(
    df: pd.DataFrame,
    imputation: str,
    fill_value,
    outlier_method: str,
    outlier_strategy: str,
    iqr_factor: float,
    zscore_thresh: float,
    subset_cols: list[str] | None,
    normalize_cols: bool,
    strip_str: bool,
    do_duplicates: bool,
    infer_dtypes: bool,
) -> tuple[pd.DataFrame, dict]:
    config = PipelineConfig(
        normalize_column_names=normalize_cols,
        str_strip=strip_str,
        drop_duplicates=do_duplicates,
        duplicate_subset=subset_cols,
        infer_dtypes=infer_dtypes,
        imputation_strategy=imputation,
        imputation_fill_value=fill_value or None,
        outliers_method=outlier_method,
        outliers_strategy=outlier_strategy,
        iqr_factor=iqr_factor,
        zscore_threshold=zscore_thresh,
    )

    df_clean, report = run_pipeline(df, config)

    return df_clean, report.summary()


if run_btn:
    df_clean, report_data = execute_pipeline(
        df_raw,
        imputation,
        fill_value,
        outlier_method,
        outlier_strategy,
        iqr_factor,
        zscore_thresh,
        subset_cols,
        normalize_cols,
        strip_str,
        do_duplicates,
        infer_dtypes,
    )

    st.session_state["df_clean"] = df_clean
    st.session_state["report_data"] = report_data


tab_original, tab_clean, tab_report = st.tabs(
    [
        ":material/table: Original Data",
        ":material/check_circle: Clean Data",
        ":material/summarize: Report",
    ]
)

with tab_original:
    st.caption(
        f"Shape: {df_raw.shape} ; types: {df_raw.dtypes.value_counts().to_dict()}"
    )

    st.dataframe(df_raw, width="stretch")

if "df_clean" in st.session_state:
    df_clean = st.session_state["df_clean"]
    report_data = st.session_state["report_data"]

    with tab_clean:
        st.caption(f"Shape: {df_clean.shape}")
        st.dataframe(df_clean, width="stretch")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "Download CSV",
                df_clean.to_csv(index=False).encode("utf-8"),
                "clean_data.csv",
                "text/csv",
                width="stretch",
                icon=":material/download:",
            )

        with col2:
            buf = io.BytesIO()
            df_clean.to_excel(buf, index=False, engine="openpyxl")
            st.download_button(
                "Download Excel",
                buf.getvalue(),
                "clean_data.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch",
                icon=":material/download:",
            )

    with tab_report:
        rows_delta = df_clean.shape[0] - df_raw.shape[0]

        m1, m2, m3, m4 = st.columns(4)

        m1.metric("Original rows", df_raw.shape[0])
        m2.metric("Clean rows", df_clean.shape[0], delta=rows_delta)
        m3.metric("Columns", df_clean.shape[1])
        m4.metric("Remaining nulls", int(df_clean.isnull().sum().sum()))

        st.json(report_data)

        nulls_before = df_raw.isnull().sum()
        nulls_after = df_clean.reindex(columns=df_raw.columns).isnull().sum()
        null_df = pd.DataFrame({"Before": nulls_before, "After": nulls_after})
        null_df = null_df[null_df["Before"] > 0]

        if not null_df.empty:
            st.subheader(":material/bar_chart: Nulls by column")
            st.bar_chart(null_df)
        else:
            st.success(
                "No nulls found in the original data", icon=":material/check_circle:"
            )

else:
    with tab_clean:
        st.info(
            "Configure options in the sidebar and click **Run cleaning**",
            icon=":material/info:",
        )
    with tab_report:
        st.info("Run the pipeline to view the report", icon=":material/pending:")
