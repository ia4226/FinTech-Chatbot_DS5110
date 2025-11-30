# Pipeline Visual Diagrams

## System Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                    FINANCIAL INTELLIGENCE PIPELINE                     │
└────────────────────────────────────────────────────────────────────────┘

                            USER INTERFACE LAYER
                                  ┌─────┐
                                  │start.py│   Interactive menu
                                  │pipeline.py│ Direct execution
                                  └─────┘

                         ↓

                  INPUT PROCESSING LAYER
              ┌──────────────────────────────┐
              │  Query Interpretation        │
              │  - Natural language parsing  │
              │  - Text normalization        │
              └──────────────────────────────┘
                            ↓

                    COMPANY EXTRACTION
              ┌──────────────────────────────┐
              │ backend/extract_company_name │
              │ - Load S&P 500 database      │
              │ - Apply matching strategies  │
              │ - Fuzzy matching & NER       │
              │ Output: Company name         │
              └──────────────────────────────┘
                            ↓
            ┌───────────────────────────────┐
            │                               │
            ▼                               ▼
    ┌──────────────────┐        ┌──────────────────┐
    │  NEWS FETCHING   │        │  STOCK FETCHING  │
    │  (Parallel)      │        │  (Parallel)      │
    └──────────────────┘        └──────────────────┘
            │                               │
            ▼                               ▼
    ┌──────────────────┐        ┌──────────────────┐
    │ BBC News Search  │        │    yfinance      │
    │ Extract Links    │        │  Get Metrics     │
    │ Fetch Articles   │        │  Format Data     │
    │ Clean Content    │        │                  │
    └──────────────────┘        └──────────────────┘
            │                               │
            ▼                               ▼
    ┌──────────────────┐        ┌──────────────────┐
    │  SUMMARIZATION   │        │ Stock Data Dict  │
    │ BART Model       │        │ - Ticker         │
    │ Chunk text       │        │ - Price          │
    │ Summarize chunks │        │ - Market cap     │
    │ Combine results  │        │ - Sector         │
    │ News Summaries   │        │ - etc.           │
    └──────────────────┘        └──────────────────┘
            │                               │
            └───────────────────────────────┘
                            ↓

                      DATA AGGREGATION
              ┌──────────────────────────────┐
              │ Combine into JSON structure  │
              │ - Company name               │
              │ - Stock information          │
              │ - News summaries             │
              │ - Timestamp                  │
              │ Output: Aggregated report    │
              └──────────────────────────────┘
                            ↓

                      AI ANALYSIS LAYER
              ┌──────────────────────────────┐
              │  OpenRouter API Call         │
              │  Model: Grok 4.1             │
              │  Task: Generate analysis     │
              │  - Company overview          │
              │  - Stock analysis            │
              │  - Market position           │
              │  - Insights & recommendations│
              │  - Risk factors              │
              │  Output: Detailed report     │
              └──────────────────────────────┘
                            ↓

                        OUTPUT LAYER
              ┌──────────────────────────────┐
              │ 1. Console Display           │
              │ 2. File Export (.txt)        │
              │ 3. Timestamped filename      │
              │ 4. Formatted sections        │
              └──────────────────────────────┘
```

## Data Flow Sequence Diagram

```
User          Pipeline      Extract       News         Stock        LLM API
 │                │           │            │            │             │
 │─ Enter query ─>│            │            │            │             │
 │                │            │            │            │             │
 │                │─ Extract ─>│            │            │             │
 │                │            │            │            │             │
 │                │<─ Company ─│            │            │             │
 │                │            │            │            │             │
 │                ├──────────────────────────────────────────────────┐ │
 │                │            │                                    │ │
 │                │─ Get news ─────────────────────>│                │ │
 │                │                                  │                │ │
 │                │────────────────────── Get stock info ─>│          │ │
 │                │                                  │      │          │ │
 │                │<───────── Articles ──────────────│      │          │ │
 │                │                                  │      │          │ │
 │                │                                  │  ────────────┐ │
 │                │                                  │      │    Stock│ │
 │                │                          ┌───────────────────┘  │ │
 │                │                          │      │               │ │
 │                │<──── Summaries ──────────┘      │               │ │
 │                │                                 │               │ │
 │                │                         ────────────────┐       │ │
 │                │                                 │     Data│     │ │
 │                │────────────────── Aggregate ────────────────────>│
 │                │                                 │      │         │
 │                │<──────────────── Report ────────────────────────│
 │                │                                 │      │         │
 │<─ Display & Save ────────────────────────────────┘      │         │
 │                │                                        │         │
 └────────────────────────────────────────────────────────────────────┘
```

## Component Interaction Diagram

```
                        PIPELINE ORCHESTRATOR
                         (pipeline.py)
                              │
                ┌─────────────┼──────────────┐
                │             │              │
                ▼             ▼              ▼
        ┌─────────────┐  ┌──────────┐  ┌─────────────┐
        │  Extract    │  │  Fetch   │  │  Fetch      │
        │  Company    │  │  News    │  │  Stock      │
        │             │  │  & Sum.  │  │  Info       │
        │  Input:     │  │          │  │             │
        │  Query      │  │  Input:  │  │  Input:     │
        │             │  │  Company │  │  Company    │
        │  Output:    │  │          │  │             │
        │  Company    │  │  Output: │  │  Output:    │
        │             │  │  News    │  │  Stock      │
        │  Functions: │  │  Summaries  Data         │
        │  -load_sp500   │          │  │             │
        │  -normalize_   │  Function    Functions:   │
        # Visual Reference

        Fresh ASCII diagrams describing how the November 2025 build is wired end-to-end.

        ## 1. System architecture

        ```
        ┌─────────────────────────────────────────────────────────────┐
        │                        User Interfaces                      │
        │                                                             │
        │  CLI (run.py)        Browser SPA (frontend/static)          │
        └────────────┬──────────────────────┬──────────────────────────┘
                     │                      │
                     │                      ▼
                     │             FastAPI (frontend/app.py)
                     │                      │
                     └───────────────┬──────┴───────────────────────────
                                     │
                           src.core.pipeline module
               ┌────────────┬────────┴────────┬──────────┬─────────────┐
               │            │                 │          │             │
        extract_company  fetch_news     fetch_stock   aggregate   generate
           (spaCy +       (BBC +          info        information detailed
           fuzz)          Grok)           (yfinance    (dict)     report
                                           + DB)                  (Grok)
               │            │                 │          │             │
               ▼            ▼                 ▼          │             ▼
         data/companies  OpenRouter     PostgreSQL  in-memory    OpenRouter
                                             ▲        JSON            ▲
                                             │                       │
                                      Analysis SQL (src/core/db.py)
                                             │
                                        /api/analysis/*
        ```

        ## 2. Frontend request flow

        ```
        User clicks "Run Report"
            │
            ▼
        POST /api/report (query)
            │
            ├─ extract_company_name(query)
            ├─ fetch_news(company)
            ├─ fetch_stock_info(company)
            │     ├─ get_stock_ticker() via Grok JSON prompt
            │     ├─ yfinance lookup
            │     └─ save_stock_snapshot() → PostgreSQL
            ├─ aggregate_information()
            └─ generate_detailed_report()
                    │
                    ▼
        Response payload
        { company, stock_info, news_summaries,
          detailed_report, chart_data }
            │
            ▼
        main.js renders stock card, price chart,
        news timeline, and AI narrative.
        ```

        ## 3. Analysis tab flow

        ```
        main.js
         ├─ on nav switch → fetch('/api/analysis/options')
         │                   ▼
         │             list_analysis_queries()
         │                   ▼
         │             send card metadata (id, title, desc)
         │
         └─ on card click  → fetch(`/api/analysis/run/${id}`)
                             ▼
                         run_analysis_query()
                             │
                             ├─ Ensure stock_snapshots table exists
                             ├─ Run SQL (e.g., top_market_cap)
                             └─ Return {columns, rows}

        DOM renders a sticky table with headers derived from `columns`.
        ```

        ## 4. Database write and reuse

        ```
        fetch_stock_info()
            │
            ├─ ticker = get_stock_ticker(company)
            ├─ info = yfinance.Ticker(ticker).info
            └─ save_stock_snapshot(info)
                    │
                    ▼
            INSERT INTO stock_snapshots (...)
                    │
                    ▼
        Analysis queries (e.g., top_market_cap)
                    │
                    ▼
        FastAPI /api/analysis/run/{id}
                    │
                    ▼
        SPA Analysis table (latest insights)
        ```

        ## 5. Testing map

        ```
        pytest
         │
         ├─ tests/test_pipeline.py
         │    ├─ import src.modules.*
         │    ├─ exercise extractor/news/stock functions
         │    └─ asserts formats without touching DB
         │
         └─ tests/test_db_connection.py   (requires .env secrets)
              ├─ ensure psycopg can SELECT 1
              ├─ run get_stock_ticker() via OpenRouter
              ├─ fetch_stock_info() (monkeypatch ticker to avoid double LLM hit)
              └─ confirm row exists in stock_snapshots
        ```

        ## 6. Lifecycle timeline (per query)

        ```
        0.0s  : CLI/SPA receives text
        0.1s  : extract_company_name resolves canonical label
        0.5s  : get_stock_ticker Grok JSON call
        1.0s  : yfinance info + DB insert
        1.5s  : BBC scraping + Grok summaries (parallel per article)
        3.0s  : aggregate_information builds payload
        3.2s  : generate_detailed_report Grok call (structured prompt)
        3.8s  : Response returned to CLI/SPA
        4.0s+ : UI renders cards + tables, CLI writes output/*.txt
        ```

        Keep these diagrams nearby when reasoning about changes—they reflect the authoritative wiring for the FastAPI UI, the AI pipeline, and the persistence layer.
        "dayLow": 149.00,
