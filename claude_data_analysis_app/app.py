"""
PM Data Analyst — AI-powered data analysis tool
Supports single files, multiple files, and full folder ingestion.
Claude generates SQL (with JOINs across tables), DuckDB executes it, Plotly visualises it.
"""

import streamlit as st
import pandas as pd
import duckdb
import json
import re
import io
import os
import glob
from anthropic import Anthropic

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PM Data Analyst",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem 2rem; border-radius: 12px;
        margin-bottom: 1.5rem; color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; }
    .main-header p  { margin: 0.25rem 0 0; opacity: 0.85; font-size: 1rem; }

    .metric-card {
        background: #f8f9ff; border: 1px solid #e0e4f7;
        border-radius: 10px; padding: 1rem 1.2rem; text-align: center;
    }
    .metric-card .label { font-size: 0.75rem; color: #6b7280;
        text-transform: uppercase; letter-spacing: .05em; }
    .metric-card .value { font-size: 1.6rem; font-weight: 700; color: #4338ca; }

    .table-chip {
        display: inline-block; background: #ede9fe; color: #5b21b6;
        border-radius: 6px; padding: 2px 10px; font-size: 0.8rem;
        font-family: monospace; margin: 2px;
    }
    .table-card {
        border: 1px solid #e0e4f7; border-radius: 10px;
        padding: 0.75rem 1rem; margin-bottom: 0.5rem;
        background: #fafbff;
    }
    .table-card .tname { font-weight: 700; color: #4338ca; font-size: 1rem; }
    .table-card .tmeta { font-size: 0.8rem; color: #6b7280; margin-top: 2px; }

    .sql-block {
        background: #1e1e2e; border-radius: 8px; padding: 1rem 1.2rem;
        font-family: 'JetBrains Mono', monospace; color: #cdd6f4;
        font-size: 0.9rem; overflow-x: auto; border-left: 4px solid #7c3aed;
    }
    .insight-box {
        background: #f0fdf4; border: 1px solid #86efac;
        border-radius: 10px; padding: 1rem 1.2rem; margin-top: 0.5rem;
    }
    .question-history {
        background: #fafafa; border-radius: 8px; padding: 0.5rem 0.75rem;
        margin-bottom: 0.4rem; border-left: 3px solid #7c3aed; font-size: 0.875rem;
    }
    .merge-banner {
        background: #fefce8; border: 1px solid #fde047; border-radius: 10px;
        padding: 0.75rem 1rem; margin: 0.5rem 0;
    }
    div[data-testid="stExpander"] > div { border-radius: 8px; }
    .stButton > button { border-radius: 8px; font-weight: 600; }
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def sanitize_table_name(filename: str) -> str:
    """Convert a filename into a valid SQL table name."""
    name = os.path.splitext(os.path.basename(filename))[0]
    name = re.sub(r"[^a-zA-Z0-9_]", "_", name)
    if name[0].isdigit():
        name = "t_" + name
    return name.lower()


@st.cache_data(show_spinner=False)
def load_file(file_bytes: bytes, filename: str) -> pd.DataFrame:
    ext = filename.rsplit(".", 1)[-1].lower()
    buf = io.BytesIO(file_bytes)
    if ext == "csv":
        return pd.read_csv(buf)
    elif ext in ("xlsx", "xls"):
        return pd.read_excel(buf)
    elif ext == "json":
        return pd.read_json(buf)
    raise ValueError(f"Unsupported file type: .{ext}")


def load_folder(folder_path: str) -> dict[str, pd.DataFrame]:
    """Read all CSV/Excel/JSON files from a folder path on disk."""
    datasets = {}
    patterns = ["*.csv", "*.xlsx", "*.xls", "*.json"]
    found = []
    for pat in patterns:
        found.extend(glob.glob(os.path.join(folder_path, pat)))
    for fpath in sorted(found):
        try:
            ext  = fpath.rsplit(".", 1)[-1].lower()
            name = sanitize_table_name(fpath)
            if ext == "csv":
                df = pd.read_csv(fpath)
            elif ext in ("xlsx", "xls"):
                df = pd.read_excel(fpath)
            elif ext == "json":
                df = pd.read_json(fpath)
            else:
                continue
            datasets[name] = df
        except Exception as e:
            st.warning(f"Skipped {os.path.basename(fpath)}: {e}")
    return datasets


def schemas_str(datasets: dict[str, pd.DataFrame]) -> str:
    """Build a full schema description for all tables."""
    parts = []
    for tname, df in datasets.items():
        lines = [f"Table: {tname} ({len(df):,} rows, {len(df.columns)} columns)"]
        for col in df.columns:
            sample = df[col].dropna().head(3).tolist()
            lines.append(f"  - {col} ({df[col].dtype}): sample = {sample}")
        parts.append("\n".join(lines))
    return "\n\n".join(parts)


def sanitize_sql(sql: str) -> str:
    """
    Auto-correct common MySQL / generic SQL functions that DuckDB does not support.
    Applied before every query execution as a safety net.
    """
    # ── Date/time name functions ──────────────────────────────────────────────
    # DAYNAME(x)   → strftime('%A', x)
    sql = re.sub(r"\bDAYNAME\s*\(", "strftime('%A', ", sql, flags=re.IGNORECASE)
    # MONTHNAME(x) → strftime('%B', x)
    sql = re.sub(r"\bMONTHNAME\s*\(", "strftime('%B', ", sql, flags=re.IGNORECASE)

    # ── Scalar date-part functions (MySQL style) → EXTRACT ────────────────────
    # YEAR(x)  → EXTRACT(YEAR FROM x)
    sql = re.sub(r"\bYEAR\s*\(([^)]+)\)", r"EXTRACT(YEAR FROM \1)", sql, flags=re.IGNORECASE)
    # MONTH(x) → EXTRACT(MONTH FROM x)
    sql = re.sub(r"\bMONTH\s*\(([^)]+)\)", r"EXTRACT(MONTH FROM \1)", sql, flags=re.IGNORECASE)
    # DAY(x)   → EXTRACT(DAY FROM x)
    sql = re.sub(r"\bDAY\s*\(([^)]+)\)", r"EXTRACT(DAY FROM \1)", sql, flags=re.IGNORECASE)
    # HOUR(x)  → EXTRACT(HOUR FROM x)
    sql = re.sub(r"\bHOUR\s*\(([^)]+)\)", r"EXTRACT(HOUR FROM \1)", sql, flags=re.IGNORECASE)
    # MINUTE(x)→ EXTRACT(MINUTE FROM x)
    sql = re.sub(r"\bMINUTE\s*\(([^)]+)\)", r"EXTRACT(MINUTE FROM \1)", sql, flags=re.IGNORECASE)
    # WEEK(x)  → EXTRACT(WEEK FROM x)
    sql = re.sub(r"\bWEEK\s*\(([^)]+)\)", r"EXTRACT(WEEK FROM \1)", sql, flags=re.IGNORECASE)
    # QUARTER(x)→ EXTRACT(QUARTER FROM x)
    sql = re.sub(r"\bQUARTER\s*\(([^)]+)\)", r"EXTRACT(QUARTER FROM \1)", sql, flags=re.IGNORECASE)
    # DAYOFWEEK(x) → EXTRACT(DOW FROM x)
    sql = re.sub(r"\bDAYOFWEEK\s*\(([^)]+)\)", r"EXTRACT(DOW FROM \1)", sql, flags=re.IGNORECASE)
    # DAYOFYEAR(x) → EXTRACT(DOY FROM x)
    sql = re.sub(r"\bDAYOFYEAR\s*\(([^)]+)\)", r"EXTRACT(DOY FROM \1)", sql, flags=re.IGNORECASE)

    # ── Null / conditional helpers ────────────────────────────────────────────
    # IFNULL(x, y)  → COALESCE(x, y)
    sql = re.sub(r"\bIFNULL\s*\(", "COALESCE(", sql, flags=re.IGNORECASE)
    # ISNULL(x)     → (x IS NULL)
    sql = re.sub(r"\bISNULL\s*\(([^)]+)\)", r"(\1 IS NULL)", sql, flags=re.IGNORECASE)
    # NVL(x, y)     → COALESCE(x, y)
    sql = re.sub(r"\bNVL\s*\(", "COALESCE(", sql, flags=re.IGNORECASE)

    # ── Aggregation helpers ───────────────────────────────────────────────────
    # GROUP_CONCAT(x)         → string_agg(x, ',')
    sql = re.sub(r"\bGROUP_CONCAT\s*\(([^)]+)\)",
                 r"string_agg(\1, ',')", sql, flags=re.IGNORECASE)
    # GROUP_CONCAT(x SEPARATOR y) → string_agg(x, y)
    sql = re.sub(r"\bGROUP_CONCAT\s*\(([^,]+)\s+SEPARATOR\s+([^)]+)\)",
                 r"string_agg(\1, \2)", sql, flags=re.IGNORECASE)

    # ── Misc ──────────────────────────────────────────────────────────────────
    # NOW() / SYSDATE() → CURRENT_TIMESTAMP
    sql = re.sub(r"\bNOW\s*\(\s*\)", "CURRENT_TIMESTAMP", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\bSYSDATE\s*\(\s*\)", "CURRENT_TIMESTAMP", sql, flags=re.IGNORECASE)
    # DATE(x) → CAST(x AS DATE)
    sql = re.sub(r"\bDATE\s*\(([^)]+)\)", r"CAST(\1 AS DATE)", sql, flags=re.IGNORECASE)
    # DATEDIFF(a, b) → DATEDIFF('day', b, a)  — MySQL arg order is reversed vs DuckDB
    sql = re.sub(r"\bDATEDIFF\s*\(([^,]+),\s*([^)]+)\)",
                 r"DATEDIFF('day', \2, \1)", sql, flags=re.IGNORECASE)
    # STR_TO_DATE(x, fmt) → STRPTIME(x, fmt)
    sql = re.sub(r"\bSTR_TO_DATE\s*\(", "STRPTIME(", sql, flags=re.IGNORECASE)

    return sql


def run_sql(datasets: dict[str, pd.DataFrame], sql: str) -> pd.DataFrame:
    sql = sanitize_sql(sql)
    con = duckdb.connect()
    for tname, df in datasets.items():
        con.register(tname, df)
    return con.execute(sql).df()


def extract_sql(text: str) -> str:
    m = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    m = re.search(r"(SELECT\s.+?;)", text, re.DOTALL | re.IGNORECASE)
    if m:
        return m.group(1).strip()
    return text.strip()


def can_merge(datasets: dict[str, pd.DataFrame]) -> bool:
    """True if all tables share the same column names."""
    col_sets = [set(df.columns) for df in datasets.values()]
    return len(col_sets) > 1 and len(set(frozenset(s) for s in col_sets)) == 1


def merged_dataset(datasets: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Union all tables into a single 'dataset' table, adding a source column."""
    frames = []
    for name, df in datasets.items():
        tmp = df.copy()
        tmp["_source_file"] = name
        frames.append(tmp)
    return {"dataset": pd.concat(frames, ignore_index=True)}


def build_chart(result_df: pd.DataFrame, chart_config: dict):
    import plotly.express as px

    ctype = chart_config.get("type", "bar").lower()
    x     = chart_config.get("x")
    y     = chart_config.get("y")
    color = chart_config.get("color")
    title = chart_config.get("title", "Analysis")

    cols = list(result_df.columns)
    if x and x not in cols: x = cols[0]
    if y and y not in cols:
        num_c = result_df.select_dtypes("number").columns.tolist()
        y = num_c[0] if num_c else cols[-1]

    try:
        if ctype == "bar":
            fig = px.bar(result_df, x=x, y=y, color=color, title=title,
                         color_discrete_sequence=px.colors.qualitative.Vivid)
        elif ctype == "line":
            fig = px.line(result_df, x=x, y=y, color=color, title=title, markers=True)
        elif ctype == "pie":
            fig = px.pie(result_df, names=x, values=y, title=title,
                         color_discrete_sequence=px.colors.qualitative.Vivid)
        elif ctype == "scatter":
            fig = px.scatter(result_df, x=x, y=y, color=color, title=title)
        elif ctype == "histogram":
            fig = px.histogram(result_df, x=x or cols[0], title=title,
                               color_discrete_sequence=["#7c3aed"])
        elif ctype == "heatmap":
            num_df = result_df.select_dtypes("number")
            fig = px.imshow(num_df.corr(), title=title, color_continuous_scale="RdBu_r")
        else:
            fig = px.bar(result_df, x=x, y=y, title=title)

        fig.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Inter, sans-serif"), title_font_size=16,
            margin=dict(t=50, b=40, l=40, r=20),
        )
        return fig
    except Exception as e:
        st.warning(f"Chart type '{ctype}' failed ({e}). Falling back to bar chart.")
        num_c = result_df.select_dtypes("number").columns.tolist()
        cat_c = result_df.select_dtypes(exclude="number").columns.tolist()
        return px.bar(result_df, x=cat_c[0] if cat_c else cols[0],
                      y=num_c[0] if num_c else cols[-1], title=title,
                      color_discrete_sequence=px.colors.qualitative.Vivid)


# ── Claude ────────────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You are an expert data analyst assistant for Product Managers.
You write SQL for DuckDB (NOT MySQL, NOT PostgreSQL, NOT SQLite).
You will be given schemas for one or more DuckDB tables. Use the exact table names provided.
When answering a question, return ONLY a JSON object with these keys (no markdown, no extra text):

{
  "sql": "<valid DuckDB SQL — use exact table names from the schema, end with semicolon>",
  "chart": {
    "type": "<bar|line|pie|scatter|histogram|heatmap>",
    "x": "<column name>",
    "y": "<column name>",
    "color": "<column name or null>",
    "title": "<descriptive title>"
  },
  "insight": "<2-3 sentence actionable insight for a PM>"
}

=== CRITICAL: DuckDB-specific SQL rules ===

Date/time functions — use these EXACTLY, never MySQL equivalents:
  - Day name:        strftime('%A', col)              NOT DAYNAME(col)
  - Month name:      strftime('%B', col)              NOT MONTHNAME(col)
  - Year number:     EXTRACT(YEAR FROM col)           NOT YEAR(col)
  - Month number:    EXTRACT(MONTH FROM col)          NOT MONTH(col)
  - Day number:      EXTRACT(DAY FROM col)            NOT DAY(col)
  - Hour:            EXTRACT(HOUR FROM col)           NOT HOUR(col)
  - Day of week:     EXTRACT(DOW FROM col)            NOT DAYOFWEEK(col)
  - Week number:     EXTRACT(WEEK FROM col)           NOT WEEK(col)
  - Quarter:         EXTRACT(QUARTER FROM col)        NOT QUARTER(col)
  - Truncate month:  DATE_TRUNC('month', col)
  - Truncate year:   DATE_TRUNC('year', col)
  - Current time:    CURRENT_TIMESTAMP               NOT NOW()
  - Date diff:       DATEDIFF('day', start, end)     NOT DATEDIFF(end, start)
  - Cast to date:    CAST(col AS DATE)               NOT DATE(col)
  - Cast to ts:      CAST(col AS TIMESTAMP)

Null / conditional:
  - COALESCE(x, y)  NOT IFNULL or NVL
  - x IS NULL       NOT ISNULL(x)

Aggregation:
  - string_agg(col, ',')   NOT GROUP_CONCAT

Other rules:
  - Use ONLY table names from the schema — never invent table names
  - You may JOIN tables if the question requires it
  - You may UNION tables if they share the same schema
  - Always end SQL with a semicolon
  - Use uppercase SQL keywords
  - Return ONLY valid JSON
"""

def ask_claude(api_key: str, schema: str, question: str, history: list):
    client = Anthropic(api_key=api_key)
    messages = history + [{
        "role": "user",
        "content": f"Available tables:\n{schema}\n\nQuestion: {question}"
    }]
    resp = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=1500,
        system=SYSTEM_PROMPT,
        messages=messages,
    )
    raw = resp.content[0].text.strip()
    raw = re.sub(r"^```(?:json)?\s*", "", raw)
    raw = re.sub(r"\s*```$", "", raw)
    try:
        result = json.loads(raw)
    except json.JSONDecodeError:
        result = {
            "sql": extract_sql(raw),
            "chart": {"type": "bar", "x": None, "y": None, "color": None, "title": "Results"},
            "insight": "Could not parse full response — SQL extracted above."
        }
    return result, raw


# ── Session state init ────────────────────────────────────────────────────────

for key, default in [("history", []), ("qa_log", []), ("datasets", {}), ("merged", False)]:
    if key not in st.session_state:
        st.session_state[key] = default


# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    api_key = st.text_input("Anthropic API Key", type="password",
                            placeholder="sk-ant-...",
                            help="Get your key at console.anthropic.com")

    st.markdown("---")
    st.markdown("## 📁 Load Data")

    # ── Tab-style toggle for upload method ───────────────────────────────────
    load_mode = st.radio("Input method", ["Upload files", "Folder path"],
                         horizontal=True, label_visibility="collapsed")

    if load_mode == "Upload files":
        uploaded_files = st.file_uploader(
            "Drag & drop files (CSV, Excel, JSON)",
            type=["csv", "xlsx", "xls", "json"],
            accept_multiple_files=True,
            help="Upload one or more files. Each becomes its own table in DuckDB."
        )
        if uploaded_files:
            new_datasets = {}
            errors = []
            for f in uploaded_files:
                tname = sanitize_table_name(f.name)
                try:
                    df = load_file(f.read(), f.name)
                    new_datasets[tname] = df
                except Exception as e:
                    errors.append(f"{f.name}: {e}")
            if new_datasets:
                st.session_state.datasets = new_datasets
                st.session_state.merged   = False
                st.session_state.history  = []
                st.session_state.qa_log   = []
            for err in errors:
                st.error(err)

    else:  # Folder path
        folder_path = st.text_input(
            "Folder path",
            placeholder="/Users/you/data/my_csvs",
            help="Paste the full path to a folder. All CSV, Excel, and JSON files inside will be loaded."
        )
        col_load, col_clear = st.columns(2)
        load_folder_btn  = col_load.button("📂 Load folder", use_container_width=True)
        clear_folder_btn = col_clear.button("🗑 Clear", use_container_width=True)

        if load_folder_btn and folder_path:
            folder_path = folder_path.strip()
            if not os.path.isdir(folder_path):
                st.error(f"Not a valid folder: {folder_path}")
            else:
                with st.spinner("Reading files…"):
                    new_datasets = load_folder(folder_path)
                if new_datasets:
                    st.session_state.datasets = new_datasets
                    st.session_state.merged   = False
                    st.session_state.history  = []
                    st.session_state.qa_log   = []
                    st.success(f"Loaded {len(new_datasets)} file(s)")
                else:
                    st.warning("No supported files found in that folder.")

        if clear_folder_btn:
            st.session_state.datasets = {}
            st.session_state.merged   = False
            st.rerun()

    # ── Merge toggle (only when multiple tables have same schema) ─────────────
    datasets = st.session_state.datasets
    if len(datasets) > 1 and can_merge(datasets):
        st.markdown("---")
        st.markdown("### 🔗 Merge Tables")
        merge_on = st.toggle(
            "Merge all files into one table",
            value=st.session_state.merged,
            help="All files share the same columns — you can UNION them into a single 'dataset' table with a _source_file column added."
        )
        if merge_on != st.session_state.merged:
            st.session_state.merged  = merge_on
            st.session_state.history = []
            st.session_state.qa_log  = []

    # ── Loaded tables summary ─────────────────────────────────────────────────
    active_datasets = (
        merged_dataset(datasets) if st.session_state.merged and len(datasets) > 1
        else datasets
    )
    if active_datasets:
        st.markdown("---")
        st.markdown("### 🗄️ Loaded Tables")
        for tname, df in active_datasets.items():
            st.markdown(
                f'<div class="table-card">'
                f'<div class="tname">📋 {tname}</div>'
                f'<div class="tmeta">{len(df):,} rows · {len(df.columns)} cols</div>'
                f'</div>',
                unsafe_allow_html=True
            )

    # ── Question history ──────────────────────────────────────────────────────
    if st.session_state.qa_log:
        st.markdown("---")
        st.markdown("### 🕐 Question History")
        for i, qa in enumerate(reversed(st.session_state.qa_log[-8:])):
            st.markdown(
                f'<div class="question-history">Q{len(st.session_state.qa_log)-i}: {qa["question"]}</div>',
                unsafe_allow_html=True
            )
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.session_state.qa_log  = []
            st.rerun()


# ── Main area ─────────────────────────────────────────────────────────────────

st.markdown("""
<div class="main-header">
  <h1>📊 PM Data Analyst</h1>
  <p>Upload files or point to a folder — ask questions across all your data in plain English.</p>
</div>
""", unsafe_allow_html=True)

active_datasets = (
    merged_dataset(st.session_state.datasets)
    if st.session_state.merged and len(st.session_state.datasets) > 1
    else st.session_state.datasets
)

# ── Empty state ───────────────────────────────────────────────────────────────
if not active_datasets:
    st.info("👈 Upload one or more files — or paste a **folder path** — in the sidebar to get started.")
    st.markdown("### 💡 What you can ask once data is loaded:")
    examples = [
        "What are the top 10 products by revenue?",
        "Join orders and customers to find high-value segments",
        "Compare monthly totals across all uploaded files",
        "Which category has the highest average order value?",
        "Show the distribution of session durations",
        "Summarise key metrics from all tables",
    ]
    cols = st.columns(2)
    for i, ex in enumerate(examples):
        cols[i % 2].markdown(f"> *\"{ex}\"*")
    st.stop()

# ── Merge banner ──────────────────────────────────────────────────────────────
if st.session_state.merged and len(st.session_state.datasets) > 1:
    n = len(st.session_state.datasets)
    total = sum(len(d) for d in st.session_state.datasets.values())
    st.markdown(
        f'<div class="merge-banner">🔗 <b>{n} files merged</b> into a single <code>dataset</code> table '
        f'({total:,} total rows). A <code>_source_file</code> column identifies the origin of each row.</div>',
        unsafe_allow_html=True
    )

# ── Dataset preview cards ─────────────────────────────────────────────────────
for tname, df in active_datasets.items():
    with st.expander(f"🔍 Preview: **{tname}** — {len(df):,} rows × {len(df.columns)} cols",
                     expanded=len(active_datasets) == 1):
        st.dataframe(df.head(50), use_container_width=True)
        c1, c2, c3, c4 = st.columns(4)
        c1.markdown(f'<div class="metric-card"><div class="label">Rows</div><div class="value">{len(df):,}</div></div>', unsafe_allow_html=True)
        c2.markdown(f'<div class="metric-card"><div class="label">Columns</div><div class="value">{len(df.columns)}</div></div>', unsafe_allow_html=True)
        c3.markdown(f'<div class="metric-card"><div class="label">Numeric</div><div class="value">{len(df.select_dtypes("number").columns)}</div></div>', unsafe_allow_html=True)
        c4.markdown(f'<div class="metric-card"><div class="label">Nulls</div><div class="value">{df.isnull().sum().sum():,}</div></div>', unsafe_allow_html=True)
        st.markdown("##### Descriptive Statistics")
        st.dataframe(df.describe(include="all").T, use_container_width=True)

# ── Table name chips ──────────────────────────────────────────────────────────
if len(active_datasets) > 1:
    chips = " ".join(f'<span class="table-chip">{t}</span>' for t in active_datasets)
    st.markdown(f"**Available tables:** {chips}", unsafe_allow_html=True)

st.markdown("---")

# ── Question input ────────────────────────────────────────────────────────────
st.markdown("### 💬 Ask a Question About Your Data")

# Smart suggestions based on first table
first_df  = next(iter(active_datasets.values()))
num_cols  = first_df.select_dtypes("number").columns.tolist()
cat_cols  = first_df.select_dtypes(exclude="number").columns.tolist()
suggestions = []
if num_cols:
    suggestions.append(f"What is the average {num_cols[0]}?")
    suggestions.append(f"Show the top 10 rows by {num_cols[0]}")
if cat_cols and num_cols:
    suggestions.append(f"Total {num_cols[0]} grouped by {cat_cols[0]}")
if len(active_datasets) > 1:
    tnames = list(active_datasets.keys())
    suggestions.append(f"Join {tnames[0]} and {tnames[1]} and show key metrics")

if suggestions:
    st.markdown("**Suggested questions:**")
    sug_cols = st.columns(min(len(suggestions), 4))
    for i, sug in enumerate(suggestions[:4]):
        if sug_cols[i].button(f"💡 {sug}", key=f"sug_{i}"):
            st.session_state["prefill_q"] = sug

prefill  = st.session_state.pop("prefill_q", "")
question = st.text_area(
    "question",
    value=prefill,
    placeholder="e.g. What are the top 5 categories by revenue? Or: join orders and customers to find the highest LTV segment.",
    height=80,
    label_visibility="collapsed",
)

col_run, _ = st.columns([1, 5])
run_btn = col_run.button("🔍 Analyse", type="primary", use_container_width=True)

# ── Run analysis ──────────────────────────────────────────────────────────────
if run_btn:
    if not api_key:
        st.error("⚠️ Please enter your Anthropic API key in the sidebar.")
        st.stop()
    if not question.strip():
        st.error("⚠️ Please type a question first.")
        st.stop()

    schema = schemas_str(active_datasets)

    with st.spinner("🤖 Claude is thinking…"):
        try:
            result, raw_response = ask_claude(api_key, schema, question, st.session_state.history)
        except Exception as e:
            st.error(f"Claude API error: {e}")
            st.stop()

    st.session_state.history.append({
        "role": "user",
        "content": f"Available tables:\n{schema}\n\nQuestion: {question}"
    })
    st.session_state.history.append({
        "role": "assistant",
        "content": raw_response
    })
    if len(st.session_state.history) > 20:
        st.session_state.history = st.session_state.history[-20:]

    sql       = result.get("sql", "")
    chart_cfg = result.get("chart", {})
    insight   = result.get("insight", "")

    # Sanitize before execution (MySQL→DuckDB corrections)
    sql_sanitized = sanitize_sql(sql)

    try:
        result_df = run_sql(active_datasets, sql)
    except Exception as e:
        st.error(f"SQL execution error: {e}")
        st.markdown("**Raw SQL from Claude:**")
        st.code(sql, language="sql")
        if sql_sanitized != sql:
            st.markdown("**Auto-corrected SQL (still failed):**")
            st.code(sql_sanitized, language="sql")
        st.stop()

    st.session_state.qa_log.append({
        "question": question, "sql": sql,
        "insight": insight, "rows": len(result_df),
    })

    st.markdown("---")
    st.markdown(f"### 🔎 Results for: *\"{question}\"*")

    tab_chart, tab_table, tab_sql, tab_insight = st.tabs(
        ["📈 Chart", "📋 Table", "🧑‍💻 SQL", "💡 Insight"]
    )

    with tab_chart:
        if result_df.empty:
            st.warning("The query returned no rows.")
        else:
            try:
                fig = build_chart(result_df, chart_cfg)
                st.plotly_chart(fig, use_container_width=True)
            except Exception as e:
                st.error(f"Chart error: {e}")

    with tab_table:
        st.markdown(f"**{len(result_df):,} rows returned**")
        st.dataframe(result_df, use_container_width=True, height=400)
        st.download_button(
            "⬇️ Download results as CSV",
            result_df.to_csv(index=False).encode(),
            file_name="query_results.csv", mime="text/csv"
        )

    with tab_sql:
        if sql_sanitized != sql:
            st.markdown("**Executed SQL** *(auto-corrected to DuckDB syntax)*:")
            st.markdown(f'<div class="sql-block"><pre>{sql_sanitized}</pre></div>',
                        unsafe_allow_html=True)
            st.code(sql_sanitized, language="sql")
            with st.expander("🔍 Original SQL from Claude"):
                st.code(sql, language="sql")
        else:
            st.markdown("**Generated SQL:**")
            st.markdown(f'<div class="sql-block"><pre>{sql}</pre></div>', unsafe_allow_html=True)
            st.code(sql, language="sql")

    with tab_insight:
        if insight:
            st.markdown(f'<div class="insight-box">💡 {insight}</div>', unsafe_allow_html=True)
        else:
            st.info("No insight generated.")
        if not result_df.empty:
            num_res = result_df.select_dtypes("number")
            if not num_res.empty:
                st.markdown("#### Quick Stats on Results")
                st.dataframe(num_res.describe().T, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<p style='text-align:center; color:#9ca3af; font-size:0.8rem;'>"
    "PM Data Analyst · Powered by Claude + DuckDB + Plotly"
    "</p>",
    unsafe_allow_html=True
)
