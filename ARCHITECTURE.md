# System Architecture

## 1. Overview

The Financial Intelligence Pipeline ingests natural-language questions, resolves company entities, enriches the request with curated news and market data, and produces detailed AI-generated reports. The project exposes the pipeline through two entry points:

- `run.py`: CLI dashboard for analysts who prefer terminal workflows.
- `frontend/app.py`: FastAPI application that powers the browser-based Chat & Analysis interface served from `frontend/static`.

All orchestration code lives inside `src/`, keeping UI layers thin and stateless.

```
┌──────────────┐      ┌───────────────────┐      ┌─────────────────────────┐      ┌─────────────────────────────────┐
│   Frontend   │ ───▶ │ FastAPI Gateways │ ───▶ │ Core Pipeline Services │ ───▶ │ Persistence & External Providers │
│ (Static SPA) │      │  /api/* endpoints │      │  extraction/data/LLM   │      │  Postgres · OpenRouter · yfinance │
└──────────────┘      └───────────────────┘      └─────────────────────────┘      └─────────────────────────────────┘
```

## 2. Layered Design

| Layer | Technologies | Responsibilities |
|-------|--------------|------------------|
| Presentation | FastAPI, vanilla JS/HTML/CSS | Serves SPA, collects user prompts, renders charts/tables. |
| Application Services | `src/core/pipeline.py`, `frontend/app.py` | Coordinates extraction, news fetch, stock lookup, LLM calls, caching/persistence. |
| Data Acquisition | `src/modules/news_fetcher.py`, `src/modules/stock_info_formatter.py`, `yfinance`, web scraping | Pulls BBC articles, stock fundamentals, and ticker metadata. |
| Intelligence | OpenRouter (Grok 4.1 Fast) | Summarizes articles, produces long-form financial reports, validates ticker symbols. |
| Persistence & Insights | PostgreSQL (`src/core/db.py`) | Stores snapshots, exposes reusable SQL insight queries for the Analysis tab. |

## 3. Core Modules & Responsibilities

| Module | Location | Key Duties |
|--------|----------|------------|
| Company extraction | `src/modules/extract_company_name.py` | Cleans user text, runs deterministic matching + spaCy heuristics to return a canonical entity (falls back to capitalized tokens). |
| News fetcher | `src/modules/news_fetcher.py` | Scrapes BBC search results, extracts article body text, removes duplicates, and enforces basic quality gates (length, timeouts). |
| Stock formatter | `src/modules/stock_info_formatter.py` | Wraps `yfinance` to normalize metrics into labeled sections for downstream display. |
| Pipeline orchestrator | `src/core/pipeline.py` | Runs end-to-end flow: extraction → news summaries → ticker validation via LLM → yfinance pull → DB persistence → OpenRouter report generation → disk export. |
| Database utilities | `src/core/db.py` | Manages `stock_snapshots`, idempotent table creation, snapshot inserts, and predefined analytical SQL queries surfaced by the Analysis UI cards. |
| Web gateway | `frontend/app.py` | Exposes `/api/*` endpoints, injects `src` package into path, serves static UI, proxies user actions into pipeline functions, and handles chart/analysis aggregation. |
| CLI shell | `run.py` | ASCII menu that invokes pipeline subcommands, documentation viewer, and targeted component tests. |

## 4. Database & Persistence

- **Engine**: PostgreSQL (configured via `DATABASE_URL`).
- **Primary table**: `stock_snapshots` with raw JSON payloads plus typed columns for prices, valuation ratios, and metadata. Records are appended for each pipeline run (no destructive updates).
- **Ingestion path**: `pipeline.fetch_stock_info()` → `save_stock_snapshot()` which lazily ensures the table exists before inserting.
- **Analysis queries**: `src/core/db.py` exposes `list_analysis_queries()` and `run_analysis_query()` powering `/api/analysis/*`. SQL snippets leverage a `latest` CTE to provide current metrics per ticker (market-cap leaders, dividend yields, sector aggregates, etc.).
- **Failure mode**: if `DATABASE_URL` is missing, persistence is skipped but the rest of the pipeline continues; Analysis endpoints will return 400 until a database is configured.

## 5. HTTP & CLI Entry Points

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serves `frontend/static/index.html` SPA (Chat + Analysis tabs). |
| `/api/extract` | POST | Body `{ "query": str }`; returns detected company used by UI auto-fill. |
| `/api/news` | POST | Body `{ "company": str }`; triggers pipeline news summarization for preview cards. |
| `/api/stock` | POST | Body `{ "company": str }`; returns formatted yfinance snapshot and persists it. |
| `/api/stock/history` | POST | Fetches 1y price history (close values) for charts, auto-resolving tickers when needed. |
| `/api/report` | POST | Full orchestration: extraction → news → stock → chart data → AI report (used by Chat tab). |
| `/api/analysis/options` | GET | Enumerates SQL insight cards available to the Analysis tab. |
| `/api/analysis/run/{id}` | GET | Runs a specific predefined SQL, returning column names and rows for dynamic tables.

The CLI menu in `run.py` mirrors this functionality for local power users (generate report, inspect extraction, run tests, open docs).

## 6. Data Flow

1. **User Prompt**: Sent from SPA or CLI to `/api/report`/`run_pipeline`.
2. **Extraction**: `extract_company_name()` uses deterministic matches + spaCy NER to normalize the entity.
3. **News Enrichment**: `pipeline.fetch_news()` combines BBC scraping with Grok summaries (chunks >1,500 chars are summarized iteratively).
4. **Ticker Validation**: `pipeline.get_stock_ticker()` asks Grok for a strict JSON ticker and falls back to user input on failure.
5. **Market Data**: `pipeline.fetch_stock_info()` calls `yfinance`, coerces fields, persists snapshots to PostgreSQL, and returns user-facing metrics.
6. **Aggregation**: `pipeline.aggregate_information()` bundles company name, stock info, news, and timestamps.
7. **LLM Report**: `pipeline.generate_detailed_report()` crafts a structured analyst brief using OpenRouter Grok 4.1 Fast.
8. **Delivery**: FastAPI responds with JSON for UI rendering; CLI prints to console and writes `output/report_<company>_<date>.txt`.

## 7. Dependencies

- **Runtime**: Python 3.11+, FastAPI, Uvicorn, Pydantic, Requests, BeautifulSoup4, Newspaper3k, feedparser, yfinance, psycopg, python-dotenv.
- **AI/LLM**: `openai` SDK targeting OpenRouter endpoints (Grok). Summaries and ticker validation use chat-completions.
- **NLP**: spaCy (English model) for entity detection inside the extractor module.
- **Visualization**: Frontend relies on Chart.js (bundled in `frontend/static`) and lightweight vanilla JS for state management.
- **Testing**: Pytest with fixtures in `tests/`.

## 8. Configuration

- `.env` (copy from `.env.example`):
	- `OPENROUTER_API_KEY`: required for Grok summarization/reporting + ticker validation.
	- `OPENAI_BASE_URL`: defaults to `https://openrouter.ai/api/v1`.
	- `DATABASE_URL`: PostgreSQL connection string (`postgresql://user:pass@host:5432/db`).
- Optional environment flags can be injected via VS Code launch configs or `uvicorn --env-file`.
- Static assets served from `frontend/static`; ensure relative paths remain valid when deploying behind a reverse proxy.

## 9. Testing & Quality Gates

- `tests/test_pipeline.py`: smoke-tests extraction, news fetcher, and aggregation helpers (with network mocked/stubbed where feasible).
- `tests/test_db_connection.py`: verifies PostgreSQL connectivity and table creation logic when `DATABASE_URL` is populated.
- `tests/ticker_test.py`: guards LLM ticker parsing and fallback behavior.
- Run `pytest` (recommended) or use the CLI option “Run Component Tests”.
- Observability: pipeline prints structured `[FETCHING]`, `[NEWS]`, `[DB]`, `[REPORT]` logs to stdout; FastAPI relies on standard Uvicorn access logs.

## 10. Security & Compliance

- Secrets are loaded from `.env` and never committed; FastAPI responses omit API keys and DB credentials.
- The project does not store user prompts unless a report file is generated manually under `output/`.
- PostgreSQL table contains only market data returned by `yfinance`; no PII is ingested.
- Network calls honor 10-second timeouts to avoid hanging resources.
- When deploying remotely, serve FastAPI behind TLS termination (nginx/Traefik) and restrict DB access via security groups or firewall rules.

## 11. Extension Guidelines

1. **Add a new news provider**: implement another fetcher in `src/modules`, return a list of article bodies, and merge results inside `pipeline.fetch_news()`.
2. **New analysis card**: append SQL to `ANALYSIS_QUERIES` in `src/core/db.py`; FastAPI automatically exposes it through `/api/analysis/options`.
3. **Alternative LLM**: update `OPENAI_BASE_URL`, change `model` IDs in `pipeline.summarize_with_grok()` and `pipeline.generate_detailed_report()`, and adjust prompt templates as needed.
4. **Enhanced UI widget**: extend `frontend/static/js/app.js` (or equivalent) to hit existing APIs; no backend changes required unless new data is needed.
5. **Batch/cron ingestion**: create a small scheduler that calls `pipeline.run_pipeline()` with a list of companies and relies on the DB snapshots for historical views.

Keep modules decoupled (pure functions, limited shared state) so that new providers or models can be swapped without touching FastAPI or the CLI entry points.
