# 📊 PM Data Analyst

> Ask questions about your data in plain English — get SQL, charts & insights instantly.

**Live app:** [claudedataanalysis.streamlit.app](https://claudedataanalysis.streamlit.app/)

---

## Overview

PM Data Analyst is a Streamlit application built for Product Managers who need to explore datasets without writing code. Upload any CSV, Excel, or JSON file (or point to a full folder), ask a question in plain English, and Claude translates it into DuckDB SQL, executes it in-memory, and returns an interactive chart, a results table, and a business-focused insight.

---

## Features

| | Feature | Description |
|---|---|---|
| 📁 | **Multi-file ingestion** | Upload individual files or paste a folder path to load every CSV/Excel/JSON at once |
| 🗄️ | **Per-file tables** | Each file becomes its own DuckDB table — named after the filename — enabling JOINs across files |
| 🔗 | **Smart merge** | If all files share the same columns, one toggle UNIONs them into a single table with a `_source_file` column |
| 🤖 | **AI-generated SQL** | Claude translates plain-English questions into DuckDB SQL including CTEs, JOINs, and date aggregations |
| 📈 | **Auto charts** | Bar, line, pie, scatter, histogram, or heatmap — Claude picks the best fit, Plotly renders it interactively |
| 💡 | **PM insights** | Each result includes a 2–3 sentence business-focused takeaway written for non-technical stakeholders |
| ⬇️ | **Export results** | Download any query result as a CSV with a single click |
| 🕐 | **Conversation memory** | Follow-up questions remember earlier context so you can drill down without re-uploading data |

---

## Quick Start (Local)

> **Prerequisites:** Python 3.9+, `pip3`, and an [Anthropic API key](https://console.anthropic.com)

```bash
# 1. Navigate to the project folder
cd ~/Desktop/Claude\ Data\ analysis\ /pm_data_analyst

# 2. Install dependencies and launch
bash launch.sh

# 3. Open in your browser
open http://localhost:8501
```

Then in the sidebar: paste your Anthropic API key, upload a file or enter a folder path, and start asking questions.

**Alternative — manual install:**
```bash
pip3 install streamlit pandas duckdb anthropic plotly openpyxl
python3 -m streamlit run app.py
```

---

## Loading Data

### Option A — Upload files

Use the sidebar file picker to drag and drop one or more CSV, Excel, or JSON files. Each file becomes its own DuckDB table named after the filename (special characters replaced with underscores). Files with different schemas can be loaded at the same time.

### Option B — Folder path

Switch the sidebar toggle to **Folder path**, paste the full path to a directory, and click **Load folder**. The app reads every CSV, Excel, and JSON file at the top level of that folder.

```
/Users/paarmita/Downloads/olist_dataset
```

> 📌 Sub-folders are not scanned — only files directly inside the target folder are loaded.

### Merging files with the same schema

When all loaded files share identical column names, a **Merge all files into one table** toggle appears. Enabling it UNIONs all files into a single `dataset` table and adds a `_source_file` column so you can still filter by origin file.

---

## Asking Questions

Type a question in the main text area and click **Analyse**. The app:

1. Sends the question and column schemas to Claude
2. Receives a DuckDB SQL query, chart config, and business insight
3. Auto-corrects any MySQL-style functions to DuckDB equivalents
4. Executes the query and renders results across four tabs

### Result tabs

| Tab | What you get |
|---|---|
| 📈 **Chart** | Interactive Plotly visualisation — hover, zoom, download PNG |
| 📋 **Table** | Full results grid with one-click CSV export |
| 🧑‍💻 **SQL** | The exact query that ran, with a copy button |
| 💡 **Insight** | Plain-English business takeaway from Claude |

### Example questions

- What are the top 10 products by total revenue?
- Show me orders per day of the week
- Which customer segment has the highest average order value?
- Join orders and customers to find the top cities by sales
- Compare monthly totals across all uploaded files

---

## DuckDB SQL Reference

Claude is instructed to write DuckDB-compatible SQL. A built-in sanitizer also auto-corrects common MySQL-style functions before every query runs.

| MySQL / Generic SQL ✗ | DuckDB (correct) ✓ |
|---|---|
| `DAYNAME(col)` | `strftime('%A', col)` |
| `MONTHNAME(col)` | `strftime('%B', col)` |
| `YEAR(col)` | `EXTRACT(YEAR FROM col)` |
| `MONTH(col)` | `EXTRACT(MONTH FROM col)` |
| `DAY(col)` | `EXTRACT(DAY FROM col)` |
| `DAYOFWEEK(col)` | `EXTRACT(DOW FROM col)` |
| `NOW()` | `CURRENT_TIMESTAMP` |
| `DATE(col)` | `CAST(col AS DATE)` |
| `DATEDIFF(end, start)` | `DATEDIFF('day', start, end)` |
| `IFNULL(x, y)` | `COALESCE(x, y)` |
| `GROUP_CONCAT(col)` | `string_agg(col, ',')` |

---

## Tech Stack

| Package | Role |
|---|---|
| `streamlit` | Web UI — file upload, sidebar, tabs, widgets |
| `duckdb` | In-memory SQL engine — executes all generated queries |
| `anthropic` | Claude API client — natural language → SQL + insight |
| `pandas` | DataFrame ingestion and manipulation |
| `plotly` | Interactive charts rendered in the browser |
| `openpyxl` | Excel (`.xlsx` / `.xls`) file parsing |

---

## Project Structure

```
pm_data_analyst/
├── app.py              ← main Streamlit application
├── requirements.txt    ← Python dependencies
├── launch.sh           ← one-command install + run script
└── README.md           ← this file
```

---

## Privacy & Security

🔒 **Your data never leaves your machine.** DuckDB runs entirely in-memory — only column names and a few sample values are sent to Claude to generate the SQL query. Raw row data is never transmitted.

- API key is entered at runtime and never stored to disk
- All results are processed locally and discarded when the session ends
- For the cloud deployment, rotate your API key regularly

---

## Deployed App

The app is live at **[claudedataanalysis.streamlit.app](https://claudedataanalysis.streamlit.app/)** — no local installation required. Visitors supply their own Anthropic API key in the sidebar.

> ⚠️ On the cloud deployment, **folder-path loading is unavailable** (the server has no access to your local filesystem). Use the file uploader instead.

---

*Powered by Claude · DuckDB · Plotly · Streamlit*
