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
        │   text         │  -get_news   -get_stock   │
        │  -clean_text   │  -summarize  -format      │
        │  -extract_     │             │             │
        │   company_name │             │             │
        └─────────────┘  └──────────┘  └─────────────┘
                │             │              │
                └─────────────┼──────────────┘
                              │
                        AGGREGATION
                        (Combine data)
                              │
                      ┌───────────────┐
                      │ AI Report Gen │
                      │               │
                      │ Input:        │
                      │ -Stock info   │
                      │ -News summary │
                      │ -Company name │
                      │               │
                      │ Output:       │
                      │ Detailed      │
                      │ Report text   │
                      └───────────────┘
                              │
                ┌─────────────┼──────────────┐
                │             │              │
                ▼             ▼              ▼
            CONSOLE       FILE SAVE       COMPLETION
            DISPLAY       (timestamped)   MESSAGE
```

## Pipeline Execution Timeline

```
START
  │
  ├─ [0.1s] Load configuration
  │
  ├─ [0.5s] Initialize extraction module
  │           └─ Load S&P 500 list (companies.csv)
  │
  ├─ [1s]   User enters query
  │
  ├─ [0.1s] Extract company name
  │           ├─ Try exact match
  │           ├─ Try token match
  │           ├─ Try fuzzy match
  │           └─ Return: "Apple Inc"
  │
  ├─ [0.5s] Initialize models
  │           ├─ Load spacy NER
  │           ├─ Load BART summarizer (lazy)
  │           └─ Initialize yfinance
  │
  ├─ [10-15s] Fetch news articles (parallel)
  │           ├─ Search BBC News
  │           ├─ Extract 5 article links
  │           └─ Fetch article content
  │
  ├─ [1-3s]  Fetch stock data (parallel)
  │           ├─ Query yfinance
  │           ├─ Extract metrics
  │           └─ Format by category
  │
  ├─ [30-60s] Summarize articles
  │           ├─ Load BART model (first run only)
  │           ├─ Chunk articles
  │           ├─ Summarize each chunk
  │           └─ Combine summaries
  │
  ├─ [1s]    Aggregate data
  │           └─ Combine into report object
  │
  ├─ [10-30s] Generate AI report
  │           ├─ Create prompt
  │           ├─ Call OpenRouter API
  │           ├─ Wait for response
  │           └─ Format sections
  │
  ├─ [0.5s]  Save to file
  │           └─ Create report_Company_Date.txt
  │
  ├─ [0.5s]  Display results
  │           └─ Print report to console
  │
  └─ END
  
  Total time: 2-5 minutes (first run)
             1-3 minutes (subsequent runs)
```

## Error Handling Flow

```
                    TRY OPERATION
                         │
              ┌──────────────────────────┐
              │                          │
              ▼                          ▼
          SUCCESS?                   EXCEPTION?
              │                          │
              YES                        NO
              │                          │
              ▼                          ▼
          CONTINUE           ┌──────────────────────┐
                             │  Log Error Message   │
                             │  - Component name    │
                             │  - Error details     │
                             └──────────────────────┘
                                      │
                             ┌────────────────────┐
                             │ Can continue?      │
                             └────────────────────┘
                                   │         │
                                  YES       NO
                                   │         │
                                   ▼         ▼
                              CONTINUE    ABORT
                              (partial)
```

## Data Structure Diagrams

### Stock Info Structure
```
stock_info = {
    "Company Info": {
        "symbol": "AAPL",
        "longName": "Apple Inc",
        "industry": "Consumer Electronics",
        "sector": "Technology",
        "website": "https://www.apple.com"
    },
    "Market Data": {
        "currentPrice": 150.25,
        "marketCap": 2500000000000,
        "dayHigh": 151.50,
        "dayLow": 149.00,
        "regularMarketChangePercent": 1.25
    },
    "Valuation Metrics": {
        "trailingPE": 28.5,
        "priceToBook": 45.2,
        "beta": 1.15
    },
    # ... more sections
}
```

### Aggregated Report Structure
```
report = {
    "company_name": "Apple Inc",
    "stock_information": {
        "Company Info": {...},
        "Market Data": {...},
        # ... all stock data
    },
    "news_summaries": [
        "Summary of article 1...",
        "Summary of article 2...",
        "Summary of article 3..."
    ],
    "timestamp": "2025-11-23T10:30:45.123456"
}
```

## File I/O Diagram

```
INPUT FILES
    │
    ├─ datasets/companies.csv
    │   └─ Used by: extract_company_name
    │       └─ Purpose: Load S&P 500 list
    │
    └─ (None - data from APIs)

OUTPUT FILES
    │
    ├─ report_<COMPANY>_<DATE>.txt
    │   ├─ Created by: pipeline.py
    │   ├─ Location: Project root
    │   ├─ Format: Text (plaintext)
    │   └─ Contains:
    │       ├─ Stock Information section
    │       ├─ Recent News Summaries section
    │       └─ Detailed Analysis section
    │
    └─ Console output (also displayed)
```

## Component Dependency Graph

```
pipeline.py (Main)
    │
    ├─ extract_company_name.py
    │   ├─ spacy (NLP)
    │   ├─ pandas (CSV loading)
    │   └─ difflib (Fuzzy matching)
    │
    ├─ news_fetcher.py
    │   ├─ requests (HTTP)
    │   ├─ BeautifulSoup (HTML parsing)
    │   ├─ feedparser (RSS parsing)
    │   └─ newspaper3k (Article extraction)
    │
    ├─ stock_info_formatter.py
    │   └─ yfinance (Stock data)
    │
    ├─ transformers (BART)
    │   └─ torch (Deep learning)
    │
    └─ openai (LLM API)
        └─ requests (HTTP)
```

## State Machine Diagram

```
    START
      │
      ▼
  IDLE
    │
    │─ User input provided
    │
    ▼
  PROCESSING_INPUT
    │
    │─ Extract company
    │
    ▼
  COMPANY_EXTRACTED / NO_COMPANY_FOUND
    │                        │
    (success)            (error)
    │                        │
    ▼                        ▼
  FETCHING_DATA      ERROR_HANDLER
    │                        │
    ├─ Fetch news           │
    ├─ Fetch stock          │
    │                        │
    ▼                        ▼
  SUMMARIZING         ABORT / RETRY
    │
    │─ Summarize articles
    │
    ▼
  AGGREGATING
    │
    │─ Combine data
    │
    ▼
  GENERATING_REPORT
    │
    │─ Call AI API
    │
    ▼
  REPORT_GENERATED
    │
    │─ Save to file
    │─ Display output
    │
    ▼
  COMPLETE
    │
    └─ Return to IDLE
```

These diagrams provide visual understanding of:
- System architecture and components
- Data flow through the pipeline
- Component interactions
- Execution timeline
- Error handling strategy
- Data structures
- File I/O operations
- Component dependencies
- State transitions
