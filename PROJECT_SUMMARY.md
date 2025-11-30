# Project Summary

The FinTech Chatbot has evolved from a standalone script into a full stack application that combines AI-assisted research, a browser-based workflow, and persistent analytics. This document captures the current scope (November 2025) so stakeholders can quickly understand what exists, how it fits together, and where to extend it.

## What the system delivers

1. **Pipeline Orchestrator (`src/core/pipeline.py`)**
    - Runs the multi-step workflow (extract → news → stock → aggregate → AI analysis).
    - Persists outputs to disk (`output/report_*.txt`) and to PostgreSQL.
    - Wraps third-party calls (OpenRouter, BBC, yfinance) with defensive logging.

2. **Database + Insight Layer (`src/core/db.py`)**
    - Automatically creates `stock_snapshots` and stores every yfinance payload for auditability.
    - Exposes 12+ predefined SQL analyses (top market cap, sector averages, recency checks, etc.).
    - Powers the Analysis tab inside the UI.

3. **FastAPI Gateway (`frontend/app.py`)**
    - Serves the static SPA (`frontend/static/*`).
    - Provides JSON endpoints (`/api/report`, `/api/news`, `/api/stock`, `/api/analysis/*`).
    - Handles ticker history lookups for charting via `yfinance`.

4. **Single-page Frontend (`frontend/static/index.html`, `main.js`, `style.css`)**
    - Chat tab for conversational requests (news, stock breakdown, chart).
    - Analysis tab that lists SQL-driven cards and renders tables dynamically.
    - Reports tab placeholder for future storytelling output.

5. **Test Harness (`tests/`)**
    - `test_pipeline.py` validates extractor/news/stock components.
    - `test_db_connection.py` is an opt-in integration suite that exercises PostgreSQL persistence plus OpenRouter ticker resolution.
    - `ticker_test.py` provides lightweight sanity checks around ticker handling.

## High-level architecture

```
User (CLI or Browser)
    │
    ├── CLI (run.py) ──> src.core.pipeline ──> output/*.txt
    │
    └── Browser SPA ──> FastAPI (frontend/app.py)
                                ├─ /api/report ──> pipeline functions
                                ├─ /api/news   ──> fetch_news
                                ├─ /api/stock  ──> fetch_stock_info
                                └─ /api/analysis/* ──> src.core.db SQL

Pipeline internals
    ├─ extract_company_name (spaCy + CSV + heuristics)
    ├─ fetch_news (BBC + OpenRouter summaries)
    ├─ get_stock_ticker (OpenRouter JSON-only prompt)
    ├─ fetch_stock_info (yfinance + snapshot persistence)
    ├─ aggregate_information (in-memory dict)
    └─ generate_detailed_report (Grok 4.1 completion)
```

## Data + configuration

- `.env` drives every secret: `OPENROUTER_API_KEY`, `OPENAI_BASE_URL`, and `DATABASE_URL`.
- `data/companies.csv` contains the canonical S&P 500 list for extraction.
- PostgreSQL stores historical stock snapshots plus feeds the Analysis queries.
- Reports are stored locally inside `output/` for traceability.

## External dependencies

| Purpose | Service/library |
|---------|-----------------|
| NLP extraction | spaCy `en_core_web_sm`, `difflib`, `pandas` |
| News content | `requests`, `beautifulsoup4`, `feedparser` scraping BBC results |
| News summarization | OpenRouter (Grok 4.1 fast) via `openai` SDK |
| Stock data | `yfinance` + `pandas` |
| Persistence | PostgreSQL via `psycopg[binary]` |
| UI | FastAPI + vanilla JS + Chart.js |

## Quality and validation

- **Automated tests**: `pytest tests/test_pipeline.py` (fast), `pytest tests/test_db_connection.py` (integration, requires API keys + DB). Both live in CI-ready form.
- **Manual validation**: Launch FastAPI + SPA to confirm chat and analysis flows; the Analysis tab only shows data once snapshots have been persisted.
- **Logging**: Every pipeline phase prints bracketed messages (e.g., `[FETCHING NEWS]`, `[DB]`) to simplify debugging inside the CLI and server logs.

## Operating the system

1. Install deps and configure `.env` (see `PIPELINE_README.md`).
2. Run `uvicorn frontend.app:app --reload` for the UI or `python run.py` for CLI.
3. To warm the database, run a few chat/report requests so that `stock_snapshots` gains rows.
4. Use the Analysis tab to confirm SQL queries succeed (no data returns `No data returned for this analysis`).
5. Execute `pytest` suites before pushing changes to keep regressions out.

## Recently completed milestones

- ✅ Persist every stock request into PostgreSQL and surface 12 canned insights.
- ✅ Ship a modern SPA with chat, charts, and database-backed analytics under the Analysis sidebar tab.
- ✅ Wire FastAPI routes that mirror the CLI pipeline, enabling both interfaces to stay in sync.
- ✅ Add integration tests that call the real ticker lookup path and assert DB writes.
- ✅ Normalize project documentation (this file + PROJECT_STRUCTURE + PIPELINE_README).

## Known limitations / next steps

1. Reports tab currently displays a placeholder; future work could embed the AI transcript there.
2. BBC-only news source occasionally misses niche tickers; consider layering in Reuters or Yahoo Finance news APIs.
3. Database writes happen per request; a background scheduler or job queue could optimize throughput for batch workloads.
4. Caching ticker lookups would lower the number of OpenRouter calls made in a single session.
5. Add alerting or retry logic if OpenRouter or yfinance temporarily fail.

## How to contribute

1. Review `PROJECT_STRUCTURE.md` for navigation.
2. Create a feature branch from `dev`.
3. Update docs/tests alongside code.
4. Run both pytest suites and, when relevant, manual UI verification.
5. Open a PR summarizing functional changes plus any DB migrations or env additions.

Use this summary as the grounding document when briefing stakeholders or onboarding collaborators; it captures both the functional wins and the guardrails needed to keep the system healthy.
