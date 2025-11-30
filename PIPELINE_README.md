# FinTech Chatbot - Pipeline Reference

This document is the authoritative guide for the Python pipeline that powers both the CLI experience (`run.py`) and the FastAPI web tier (`frontend/app.py`). Use it to understand how every request traverses the system, what external services are touched, and how to operate or extend the stack safely.

## Capabilities at a glance

- Natural-language company extraction with spaCy, fuzzy heuristics, and an S&P 500 lookup table (`data/companies.csv`).
- BBC news retrieval plus Grok-powered summarization to condense multi-paragraph articles into actionable bullets.
- Real-time market data via `yfinance`, normalized into a predictable dictionary and persisted to PostgreSQL.
- AI-assisted insight generation (OpenRouter Grok 4.1) that synthesizes metrics + news into a structured report.
- FastAPI endpoints that expose the same pipeline to the single-page browser UI, including SQL-driven analysis cards backed by the snapshot database.

## Technology stack

| Layer | Details |
|-------|---------|
| Language/runtime | Python 3.12 (virtual environment stored in `venv/`) |
| Core libs | `fastapi`, `uvicorn`, `psycopg[binary]`, `yfinance`, `spacy`, `beautifulsoup4`, `openai` (for OpenRouter client) |
| Frontend | Vanilla HTML/CSS/JS + Chart.js, bundled as a static SPA served by FastAPI |
| Database | PostgreSQL (connection string supplied via `DATABASE_URL`) |
| External APIs | BBC News pages, Yahoo Finance, OpenRouter (Grok models) |

## Environment & installation

1. **Create/activate a virtual environment**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```
2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   python -m spacy download en_core_web_sm
   ```
3. **Configure `.env`** (copy from `.env.example`):
   - `OPENROUTER_API_KEY`: key from https://openrouter.ai
   - `OPENAI_BASE_URL`: default `https://openrouter.ai/api/v1`
   - `DATABASE_URL`: e.g. `postgresql://postgres:postgres@localhost:5432/fintech`

## Running the pipeline

### Interactive CLI
```bash
python run.py                 # shows a menu for extract/news/stock/full report
python -m src.core.pipeline   # run the report workflow directly
```
Each run produces `output/report_<company>_<date>.txt` containing stock metrics, news summaries, and the AI analysis transcript.

### FastAPI + SPA
```bash
uvicorn frontend.app:app --reload
# Navigate to http://127.0.0.1:8000 to access Chat, Analysis, and (future) Reports tabs.
```
The frontend talks to the same pipeline functions through `/api/report`, `/api/news`, `/api/stock`, and `/api/analysis/*` endpoints.

## Pipeline stages

```
User query
  │
  ├─ extract_company_name()      → spaCy NER + fuzzy matching + CSV lookup
  │
  ├─ fetch_news()
  │     ├─ get_news_content()    → BBC scraping + BeautifulSoup
  │     └─ summarize_with_grok() → OpenRouter Grok 4.1
  │
  ├─ fetch_stock_info()
  │     ├─ get_stock_ticker()    → Grok JSON-only prompt
  │     ├─ yfinance.Ticker       → Fundamental & market data
  │     └─ save_stock_snapshot() → PostgreSQL `stock_snapshots`
  │
  ├─ aggregate_information()
  └─ generate_detailed_report()  → Grok 4.1 chat completion
```

### Key functions

| Function | Location | Notes |
|----------|----------|-------|
| `extract_company_name` | `src/modules/extract_company_name.py` | Combines CSV lookup, spaCy NER, and fuzzy matching for robustness. |
| `get_news_content` | `src/modules/news_fetcher.py` | Fetches up to five BBC articles, cleans HTML into paragraphs. |
| `summarize_with_grok` | `src/core/pipeline.py` | Replaces on-device models with OpenRouter for consistent bullet outputs. |
| `fetch_stock_info` | `src/core/pipeline.py` | Resolves the ticker via LLM, fetches `yfinance` info, persists a snapshot. |
| `save_stock_snapshot` | `src/core/db.py` | Creates `stock_snapshots` table on demand and inserts JSON payloads. |
| `generate_detailed_report` | `src/core/pipeline.py` | Builds multi-section analyst-style prose. |

## Database contract

`src/core/db.py` expects `DATABASE_URL` to point to PostgreSQL. The table schema:

```
stock_snapshots (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    long_name TEXT,
    sector TEXT,
    industry TEXT,
    current_price DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    trailing_pe DOUBLE PRECISION,
    dividend_yield DOUBLE PRECISION,
    week_52_high DOUBLE PRECISION,
    week_52_low DOUBLE PRECISION,
    total_revenue DOUBLE PRECISION,
    free_cashflow DOUBLE PRECISION,
    website TEXT,
    raw_payload JSONB NOT NULL,
    captured_at TIMESTAMPTZ DEFAULT NOW()
)
```

Additional helpers expose curated insight queries:

- `list_analysis_queries()` - metadata (id, title, description) used to render cards in the Analysis tab.
- `run_analysis_query(query_id)` - executes one of ~12 SQL statements (top market cap, sector averages, latest ingestions, etc.) and returns rows/columns for the frontend.

## FastAPI endpoints

| Method & Path | Description |
|---------------|-------------|
| `GET /` | Serves `frontend/static/index.html` (SPA). |
| `POST /api/report` | Full orchestration: extract → news → stock → DB → report → chart data. |
| `POST /api/news` | Returns only the news summaries (shortcut for UI). |
| `POST /api/stock` | Returns only the latest stock payload. |
| `POST /api/stock/history` | 1-year price history for charting via `yfinance`. |
| `GET /api/analysis/options` | Lists SQL insights available in the Analysis sidebar. |
| `GET /api/analysis/run/{id}` | Executes the associated SQL query and returns tabular data. |

Each endpoint wraps pipeline calls in exception handling and returns JSON suitable for the SPA.

## Testing strategy

| Test | Command | Purpose | Requirements |
|------|---------|---------|--------------|
| Component suite | `pytest tests/test_pipeline.py` | Validates extraction, news fetching, and stock formatting in isolation. | Internet for yfinance/BBC; no DB required. |
| DB integration | `pytest tests/test_db_connection.py -vv` | Verifies PostgreSQL connectivity, LLM ticker lookup, snapshot persistence, and row retrieval. | `DATABASE_URL`, `OPENROUTER_API_KEY`, reachable PostgreSQL instance. |

Use `pytest -k <name>` to focus on individual behaviours during development.

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| `OPENROUTER_API_KEY not set` | `.env` missing or not loaded. | Copy `.env.example`, fill secrets, restart shell. |
| `psycopg.errors.InvalidCatalogName` | Database referenced in `DATABASE_URL` does not exist. | Create the database (`createdb fintech`) before running the app/tests. |
| News summaries are empty | BBC blocked request or company too niche. | Retry with VPN, provide broader query, or add another news source in `news_fetcher`. |
| `/api/analysis/run/...` 500 error | Selected query requires rows but table is empty. | Run a few chat/report requests so `save_stock_snapshot` populates data. |

## Extending the pipeline

- **Additional insights**: Append SQL definitions to `ANALYSIS_QUERIES` in `src/core/db.py` and the Analysis UI picks them up automatically.
- **New data sources**: Create modules in `src/modules/` and orchestrate them inside `pipeline.py` before aggregation.
- **Alternate UI**: The same FastAPI endpoints can power another client (e.g., Streamlit or mobile) without touching pipeline code.
- **Caching**: Wrap `fetch_news` or `fetch_stock_info` with a caching layer if rate limits become an issue.

Keep this document close whenever you modify pipeline internals—the sections above outline every dependency chain you need to consider.
