import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="EDA Pro", page_icon="\U0001f4ca", layout="wide", initial_sidebar_state="expanded")

st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"], .stApp, .stMarkdown, .stButton, .stSelectbox,
.stTextInput, .stDataFrame, .stMetric, .stTabs, [data-testid="stSidebar"] {
    font-family: 'Poppins', sans-serif !important;
}

/* Headings */
h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif !important; font-weight: 600 !important; letter-spacing: -0.01em; }
h1 { font-weight: 700 !important; }

/* Sidebar */
[data-testid="stSidebar"] {
    border-right: 1px solid rgba(150,150,150,0.15);
}
[data-testid="stSidebar"] h1 { font-size: 1.35rem !important; }
[data-testid="stSidebar"] .stMarkdown p { font-weight: 500; opacity: 0.85; }

/* Metric cards */
[data-testid="stMetric"] {
    background: rgba(127,127,127,0.06);
    border: 1px solid rgba(127,127,127,0.15);
    border-radius: 12px;
    padding: 14px 16px 10px 16px;
}
[data-testid="stMetricLabel"] { font-weight: 500 !important; opacity: 0.75; letter-spacing: 0.01em; }
[data-testid='stMetricValue'] { font-size: 1.7rem; font-weight: 700; }

/* Tabs */
.stTabs [data-baseweb='tab-list'] { gap: 4px; }
.stTabs [data-baseweb='tab'] {
    font-size: 0.95rem;
    font-weight: 600;
    padding: 10px 20px;
    border-radius: 8px 8px 0 0;
}

/* Buttons */
.stButton button, .stDownloadButton button {
    font-family: 'Poppins', sans-serif !important;
    font-weight: 600 !important;
    border-radius: 8px !important;
    letter-spacing: 0.01em;
}

/* Dataframes */
[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

/* Section dividers a touch tighter */
hr { margin: 0.6rem 0 !important; opacity: 0.2; }

/* Checkbox / selectbox labels */
.stCheckbox label, .stSelectbox label, .stRadio label, .stSlider label {
    font-weight: 500 !important;
}
</style>""", unsafe_allow_html=True)

# Check once whether statsmodels is available, since plotly's trendline="ols"
# silently depends on it and otherwise throws at render time.
try:
    import statsmodels.api as _sm  # noqa: F401
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

# Palettes usable both as discrete sequences (bar/pie/box/violin) and
# continuous scales (heatmap-style color_continuous_scale).
DISCRETE_PALETTES = {
    "plotly": px.colors.qualitative.Plotly,
    "viridis": px.colors.sequential.Viridis,
    "plasma": px.colors.sequential.Plasma,
    "Set2": px.colors.qualitative.Set2,
    "pastel": px.colors.qualitative.Pastel,
}
CONTINUOUS_PALETTES = {
    "plotly": "Plotly3",
    "viridis": "Viridis",
    "plasma": "Plasma",
    "Set2": "Aggrnyl",
    "pastel": "Peach",
}


@st.cache_data
def load_sample(name):
    urls = {
        "Titanic": "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv",
        "Iris": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv",
        "Tips": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv",
        "Penguins": "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/penguins.csv",
    }
    return pd.read_csv(urls[name])


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("\U0001f4ca EDA Pro")
    st.markdown("---")
    source = st.radio("Data Source", ["Upload CSV", "Sample Dataset"])
    df_raw = None
    if source == "Upload CSV":
        f = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xlsx", "xls"])
        if f:
            try:
                if f.name.lower().endswith((".xlsx", ".xls")):
                    xls = pd.ExcelFile(f)
                    sheet = xls.sheet_names[0]
                    if len(xls.sheet_names) > 1:
                        sheet = st.selectbox("Choose sheet", xls.sheet_names)
                    df_raw = pd.read_excel(xls, sheet_name=sheet)
                else:
                    df_raw = pd.read_csv(f)
            except Exception as e:
                st.error(f"Could not read that file: {e}")
    else:
        sample_name = st.selectbox("Choose sample", ["Titanic", "Iris", "Tips", "Penguins"])
        try:
            df_raw = load_sample(sample_name)
        except Exception as e:
            st.error(f"Could not load the sample dataset (network issue?): {e}")

    palette = "plotly"
    if df_raw is not None:
        st.markdown("---")
        st.markdown("### \U0001f9f9 Data Cleaning")
        drop_empty_cols = st.checkbox(
            "Drop empty / unnamed columns",
            help="Removes columns like 'Unnamed: 7' that are entirely blank — common in CSVs exported from Excel."
        )
        drop_na = st.checkbox("Drop rows with missing values")
        drop_dup = st.checkbox("Remove duplicate rows")
        impute = st.selectbox("Impute missing values", ["None", "Mean", "Median", "Mode"])
        st.markdown("---")
        palette = st.selectbox("Color palette", ["plotly", "viridis", "plasma", "Set2", "pastel"])

# ── Main ──────────────────────────────────────────────────────────────────────
st.title("\U0001f4ca EDA Pro — Exploratory Data Analysis")

if df_raw is None:
    st.info("\U0001f448 Upload a CSV or select a sample dataset from the sidebar to begin.")
    c1, c2, c3, c4 = st.columns(4)
    c1.info("\U0001f6a2 **Titanic**\nSurvival prediction")
    c2.info("\U0001f338 **Iris**\nFlower classification")
    c3.info("\U0001f37d\ufe0f **Tips**\nRegression practice")
    c4.info("\U0001f427 **Penguins**\nClustering practice")
    st.stop()

if df_raw.shape[0] == 0 or df_raw.shape[1] == 0:
    st.error("This dataset has no rows or no columns, so there's nothing to analyze.")
    st.stop()

# ── Apply Cleaning ─────────────────────────────────────────────────────────────
df = df_raw.copy()
if drop_empty_cols:
    junk_cols = [
        c for c in df.columns
        if df[c].isnull().all() or (str(c).startswith("Unnamed:") and df[c].isnull().mean() > 0.95)
    ]
    if junk_cols:
        df = df.drop(columns=junk_cols)
        st.toast(f"Dropped {len(junk_cols)} empty/unnamed column(s)", icon="\u2705")
if drop_na:
    before = len(df)
    df = df.dropna()
    st.toast(f"Dropped {before - len(df)} rows with missing values", icon="\u2705")
if drop_dup:
    before = len(df)
    df = df.drop_duplicates()
    st.toast(f"Removed {before - len(df)} duplicate rows", icon="\u2705")
if impute != "None":
    num_cols_imp = df.select_dtypes(include="number").columns
    for c in num_cols_imp:
        if df[c].isnull().any():
            if impute == "Mean":
                df[c] = df[c].fillna(df[c].mean())
            elif impute == "Median":
                df[c] = df[c].fillna(df[c].median())
            elif impute == "Mode":
                mode = df[c].mode()
                if not mode.empty:
                    df[c] = df[c].fillna(mode.iloc[0])
    st.toast(f"Imputed missing values using {impute}", icon="\u2705")

if df.shape[0] == 0 or df.shape[1] == 0:
    st.warning("Your cleaning options removed all rows or columns. Adjust them in the sidebar to see results.")
    st.stop()

if "column_casts" not in st.session_state:
    st.session_state.column_casts = {}
invalid_casts = []
for cast_col, cast_type in st.session_state.column_casts.items():
    if cast_col in df.columns:
        try:
            if cast_type == "datetime":
                df[cast_col] = pd.to_datetime(df[cast_col])
            else:
                df[cast_col] = df[cast_col].astype(cast_type)
        except (TypeError, ValueError):
            invalid_casts.append(cast_col)
for cast_col in invalid_casts:
    del st.session_state.column_casts[cast_col]

num_cols = df.select_dtypes(include="number").columns.tolist()
cat_cols = df.select_dtypes(include="object").columns.tolist()

disc_seq = DISCRETE_PALETTES.get(palette, px.colors.qualitative.Plotly)
cont_scale = CONTINUOUS_PALETTES.get(palette, "Plotly3")

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(["\U0001f50d Overview", "\U0001f4ca Distributions", "\U0001f517 Correlations", "\U0001f9f9 Export & Cleaning"])

# ════ TAB 1: OVERVIEW ══════════════════════════════════════════════════════════
with tab1:
    mem = df.memory_usage(deep=True).sum()
    mem_str = f"{mem/1024:.1f} KB" if mem < 1024**2 else f"{mem/1024**2:.2f} MB"
    miss_total = int(df.isnull().sum().sum())
    miss_pct = round(miss_total / (df.shape[0] * df.shape[1]) * 100, 2)

    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Rows", f"{df.shape[0]:,}")
    m2.metric("Columns", df.shape[1])
    m3.metric("Missing Values", f"{miss_total:,}")
    m4.metric("Missing %", f"{miss_pct}%")
    m5.metric("Memory", mem_str)

    st.markdown("---")
    v1, v2, v3 = st.tabs(["Raw Data", "Data Types", "Missing Values"])

    with v1:
        max_rows = max(5, min(200, len(df)))
        default_rows = min(10, max_rows)
        n = st.slider("Rows to show", 5, max_rows, default_rows) if max_rows > 5 else max_rows
        st.dataframe(df.head(n), use_container_width=True)

    with v2:
        dt = pd.DataFrame({
            "Column": df.columns,
            "Type": df.dtypes.astype(str).values,
            "Non-Null": df.notnull().sum().values,
            "Null Count": df.isnull().sum().values,
            "Unique Values": df.nunique().values
        })
        st.dataframe(dt, use_container_width=True)

    with v3:
        miss = df.isnull().sum().reset_index()
        miss.columns = ["Column", "Missing Count"]
        miss["Missing %"] = (miss["Missing Count"] / len(df) * 100).round(2)
        miss = miss[miss["Missing Count"] > 0].sort_values("Missing %", ascending=False)
        if len(miss) == 0:
            st.success("\u2705 No missing values in this dataset!")
        else:
            fig = px.bar(miss, x="Column", y="Missing %", color="Missing %",
                         color_continuous_scale=cont_scale,
                         title="Missing Value % per Column", text="Missing %")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(miss, use_container_width=True)

    st.markdown("---")
    st.subheader("\U0001f4c8 Statistical Summary")
    st.dataframe(df.describe().round(3), use_container_width=True)

# ════ TAB 2: DISTRIBUTIONS ════════════════════════════════════════════════════
with tab2:
    if num_cols:
        st.subheader("Numerical Column Analysis")
        sel_num = st.selectbox("Select numeric column", num_cols, key="num_dist")
        d1, d2, d3 = st.columns(3)
        with d1:
            st.markdown("**Histogram**")
            fig = px.histogram(df, x=sel_num, marginal="box", title=f"Histogram — {sel_num}",
                               color_discrete_sequence=disc_seq)
            st.plotly_chart(fig, use_container_width=True)
        with d2:
            st.markdown("**Box Plot**")
            fig = px.box(df, y=sel_num, title=f"Box Plot — {sel_num}",
                         color_discrete_sequence=disc_seq)
            st.plotly_chart(fig, use_container_width=True)
        with d3:
            st.markdown("**Violin Plot**")
            fig = px.violin(df, y=sel_num, box=True, points="outliers",
                            title=f"Violin — {sel_num}",
                            color_discrete_sequence=disc_seq)
            st.plotly_chart(fig, use_container_width=True)

    if cat_cols:
        st.markdown("---")
        st.subheader("Categorical Column Analysis")
        sel_cat = st.selectbox("Select categorical column", cat_cols, key="cat_dist")
        top_n = st.slider("Top N categories", 3, 20, 10, key="topn")
        vc = df[sel_cat].value_counts().head(top_n).reset_index()
        vc.columns = [sel_cat, "Count"]
        ca1, ca2 = st.columns(2)
        with ca1:
            fig = px.bar(vc, x=sel_cat, y="Count", color="Count",
                         color_continuous_scale=cont_scale,
                         title=f"Top {top_n} — {sel_cat}")
            st.plotly_chart(fig, use_container_width=True)
        with ca2:
            fig = px.pie(vc, names=sel_cat, values="Count",
                         title=f"Pie Chart — {sel_cat}", hole=0.35,
                         color_discrete_sequence=disc_seq)
            st.plotly_chart(fig, use_container_width=True)

    if not num_cols and not cat_cols:
        st.warning("No columns available for distribution analysis.")

# ════ TAB 3: CORRELATIONS ═════════════════════════════════════════════════════
with tab3:
    if len(num_cols) < 2:
        st.warning("Need at least 2 numeric columns for correlation analysis.")
    else:
        st.subheader("\U0001f525 Correlation Heatmap")
        corr = df[num_cols].corr().round(2)
        fig, ax = plt.subplots(figsize=(max(8, len(num_cols)), max(6, len(num_cols) - 1)))
        sns.heatmap(corr, annot=True, fmt=".2f", cmap="coolwarm",
                    center=0, square=True, linewidths=0.5, ax=ax)
        ax.set_title("Feature Correlation Matrix", fontsize=14, pad=15)
        st.pyplot(fig)
        plt.close()

        st.markdown("---")
        st.subheader("\U0001f535 Scatter Plot Explorer")
        s1, s2, s3 = st.columns(3)
        x_col = s1.selectbox("X axis", num_cols, key="sx")
        y_col = s2.selectbox("Y axis", num_cols, index=min(1, len(num_cols) - 1), key="sy")
        hue_opts = ["None"] + cat_cols
        hue = s3.selectbox("Color by (hue)", hue_opts, key="hue")

        if not HAS_STATSMODELS:
            st.caption("Trendline disabled: install `statsmodels` to enable OLS trendlines.")

        fig = px.scatter(df, x=x_col, y=y_col,
                         color=None if hue == "None" else hue,
                         trendline="ols" if HAS_STATSMODELS else None,
                         title=f"{x_col} vs {y_col}",
                         opacity=0.7, marginal_x="histogram", marginal_y="histogram",
                         color_discrete_sequence=disc_seq)
        st.plotly_chart(fig, use_container_width=True)

        if len(num_cols) <= 6:
            st.markdown("---")
            st.subheader("\U0001f537 Pair Plot")
            hue2 = st.selectbox("Hue for pair plot", hue_opts, key="hue2")
            fig = px.scatter_matrix(df, dimensions=num_cols,
                                    color=None if hue2 == "None" else hue2,
                                    title="Pair Plot Matrix", opacity=0.6,
                                    color_discrete_sequence=disc_seq)
            fig.update_traces(diagonal_visible=False, showupperhalf=False)
            st.plotly_chart(fig, use_container_width=True)

# ════ TAB 4: EXPORT ════════════════════════════════════════════════════════════
with tab4:
    st.subheader("\U0001f4cb Column Type Casting")
    st.markdown("Dynamically change the data type of any column:")
    cast_col = st.selectbox("Select column", df.columns.tolist(), key="cast_col")
    cast_type = st.selectbox("Cast to type", ["string", "int64", "float64", "category", "datetime"], key="cast_type")
    if st.button("Apply Cast", use_container_width=True):
        try:
            cast_preview = df[cast_col].copy()
            if cast_type == "datetime":
                pd.to_datetime(cast_preview)
            else:
                cast_preview.astype(cast_type)
            st.session_state.column_casts[cast_col] = cast_type
            st.success("Column cast successfully!")
        except Exception as e:
            st.error(f"Could not cast column: {e}")

    st.dataframe(df.dtypes.rename("Type"), use_container_width=True)
    st.markdown("---")
    st.subheader("\U0001f4e5 Download Cleaned Dataset")
    st.markdown(f"**Current dataset:** {df.shape[0]:,} rows x {df.shape[1]} columns")
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    st.download_button(
        label="\u2b07\ufe0f Download Cleaned CSV",
        data=csv_buf.getvalue(),
        file_name="cleaned_dataset.csv",
        mime="text/csv",
        use_container_width=True
    )