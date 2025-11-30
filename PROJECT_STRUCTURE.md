# FinTech Chatbot - Project Structure

This repository hosts every component required to research a company, generate AI-backed analysis, serve it over a FastAPI backend, and surface results inside a polished browser UI. The folders below reflect the current (November 2025) layout after the database, frontend, and testing upgrades.

## Repository map

```
Project/
├── .env / .env.example        # Environment variables (API keys, DATABASE_URL)
├── run.py                     # Interactive CLI entry point
├── README.md                  # High-level overview (front-door doc)
├── requirements.txt           # Python dependencies
├── ARCHITECTURE.md, PROJECT_SUMMARY.md, ...  # Living docs in the root
│
├── src/
│   ├── core/
│   │   ├── pipeline.py        # LLM-driven pipeline orchestration
│   │   └── db.py              # PostgreSQL helpers + analysis SQL
│   └── modules/
│       ├── extract_company_name.py
│       ├── news_fetcher.py
│       └── stock_info_formatter.py
│
├── frontend/
│   ├── app.py                 # FastAPI app that serves the SPA + APIs
│   └── static/
│       ├── index.html         # Single-page UI (chat + analysis views)
│       ├── main.js            # Client logic (fetches APIs, renders cards)
│       └── style.css          # Tailored design system
│
├── tests/
│   ├── conftest.py            # Makes `src` importable inside pytest
│   ├── test_pipeline.py       # Component validation for CLI pipeline
│   ├── test_db_connection.py  # Integration test hitting PostgreSQL + APIs
│   └── ticker_test.py         # Utility checks around ticker lookup logic
│
├── data/
│   └── companies.csv          # S&P 500 list used by the extractor
│
├── output/                    # Saved AI reports (`report_<company>_<date>.txt`)
├── config/                    # Reserved for future env-specific configs
├── docs/                      # Additional guides (quick ref, usage guide, etc.)
├── __pycache__/, .pytest_cache/, venv/   # Tooling artifacts (can be ignored)
└── Iteration 2.pdf, diagrams, summaries  # Planning/history assets
```

## Directory highlights

| Area | Purpose | Key Artifacts |
|------|---------|---------------|
| `src/core` | Business logic. `pipeline.py` ties NLP, news, stock, and LLM calls together. `db.py` manages PostgreSQL writes plus the predefined SQL insights surfaced in the Analysis UI. | `run_pipeline`, `fetch_news`, `save_stock_snapshot`, `ANALYSIS_QUERIES` |
| `src/modules` | Reusable building blocks. | Company extractor (spaCy + fuzzy match), news fetcher (BBC scraping + summarization prep), stock formatter (yfinance). |
| `frontend` | FastAPI service + static SPA. `app.py` exposes `/api/*` endpoints and serves `static/index.html`, while `main.js` renders chat, price charts, and database-backed insight tables. | `/api/report`, `/api/analysis/options`, `/api/analysis/run/{id}` |
| `tests` | Automated confidence. Mix of fast unit tests and opt-in integration checks that call OpenRouter + PostgreSQL. | `pytest -q tests/test_pipeline.py`, `pytest tests/test_db_connection.py` |
| `data` | Reference data required for name extraction. | `companies.csv` |
| `output` | Every CLI run saves a timestamped txt report for auditing. | `report_Tesla_2025-11-30.txt` |

## Running the different surfaces

### 1. CLI / pipeline
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # then fill OPENROUTER_API_KEY, OPENAI_BASE_URL, DATABASE_URL
python run.py           # launches the interactive menu
```

### 2. FastAPI + web front-end
```bash
venv\Scripts\activate
uvicorn frontend.app:app --reload
# open http://127.0.0.1:8000 and use the Chat or Analysis sidebar tabs
```

### 3. Tests
```bash
pytest tests/test_pipeline.py              # offline-friendly component test
pytest tests/test_db_connection.py -vv     # requires DATABASE_URL + OPENROUTER_API_KEY
```

## Environment prerequisites

| Variable | Description | Location |
|----------|-------------|----------|
| `OPENROUTER_API_KEY` | Key for Grok/GPT calls used for summaries, ticker resolution, and final reports. | `.env` |
| `OPENAI_BASE_URL` | Typically `https://openrouter.ai/api/v1`; allows swapping to other providers. | `.env` |
| `DATABASE_URL` | PostgreSQL connection string for persisting snapshots + running Analysis SQL. | `.env` |

## How the pieces relate

```
run.py  ──>  src.core.pipeline
             ├─ fetch_news()        ──> src.modules.news_fetcher + OpenRouter
             ├─ fetch_stock_info()  ──> yfinance + src.core.db.save_stock_snapshot()
             ├─ aggregate_information()
             └─ generate_detailed_report() ──> OpenRouter

frontend/app.py
 ├─ Serves static UI
 ├─ /api/report            ──> pipeline (news, stock, AI report)
 ├─ /api/stock/history     ──> yfinance direct
 ├─ /api/analysis/options  ──> src.core.db.list_analysis_queries
 └─ /api/analysis/run/{id} ──> src.core.db.run_analysis_query

tests/*
 ├─ test_pipeline.py       ──> Calls pipeline functions with fixtures
 └─ test_db_connection.py  ──> Resolves tickers, persists rows, checks PostgreSQL
```

Use this file as the canonical map when onboarding new collaborators or adding a feature. Every path listed above has been verified against the current repo so you can trust it when navigating or updating documentation elsewhere.
