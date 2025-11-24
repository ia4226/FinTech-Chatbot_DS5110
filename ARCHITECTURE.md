# Architecture & Integration Guide

## System Architecture

### Overview

The Financial Intelligence Pipeline is a multi-stage system that transforms user queries into comprehensive financial reports through data aggregation, processing, and AI analysis.

```
┌──────────────────────────────────────────────────────────────────┐
│                   FINANCIAL INTELLIGENCE PIPELINE               │
│                                                                  │
│  INPUT LAYER                                                     │
│  ├─ User Query (Natural Language)                               │
│  └─ Company Names Database (S&P 500 List)                       │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ PROCESSING LAYER                                        │   │
│  │                                                          │   │
│  │  1. Company Extraction Module                           │   │
│  │     └─ Input: User query                                │   │
│  │     └─ Process: NLP + Fuzzy Matching                    │   │
│  │     └─ Output: Normalized company name                  │   │
│  │                                                          │   │
│  │  2. Data Collection Layer (Parallel)                    │   │
│  │     ├─ News Fetcher                                     │   │
│  │     │  ├─ Input: Company name                           │   │
│  │     │  ├─ Source: BBC News API                          │   │
│  │     │  └─ Output: Article texts                         │   │
│  │     │                                                    │   │
│  │     └─ Stock Info Formatter                             │   │
│  │        ├─ Input: Company ticker                         │   │
│  │        ├─ Source: yfinance (Yahoo Finance)              │   │
│  │        └─ Output: Stock metrics dictionary              │   │
│  │                                                          │   │
│  │  3. Summarization Module                                │   │
│  │     ├─ Input: Full article texts                        │   │
│  │     ├─ Model: facebook/bart-large-cnn                   │   │
│  │     └─ Output: Summarized articles                      │   │
│  │                                                          │   │
│  │  4. Data Aggregation                                    │   │
│  │     ├─ Combine: Stock info + News summaries             │   │
│  │     └─ Output: Structured report object                 │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                           │
│       ▼                                                           │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ AI ANALYSIS LAYER                                       │   │
│  │                                                          │   │
│  │  1. Report Generation                                   │   │
│  │     ├─ Input: Aggregated data + Company info            │   │
│  │     ├─ API: OpenRouter (Grok 4.1)                       │   │
│  │     └─ Output: Detailed analysis report                 │   │
│  │                                                          │   │
│  │  2. Formatting & Enrichment                             │   │
│  │     ├─ Structure: Markdown/Text format                  │   │
│  │     ├─ Sections: Overview, Analysis, Insights, Risks    │   │
│  │     └─ Output: Final report                             │   │
│  └─────────────────────────────────────────────────────────┘   │
│       │                                                           │
│       ▼                                                           │
│  OUTPUT LAYER                                                    │
│  ├─ Console Display                                             │
│  ├─ Text File (report_<Company>_<Date>.txt)                    │
│  └─ JSON Report Object                                          │
└──────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Company Extraction (`backend/extract_company_name.py`)

**Purpose**: Convert natural language queries to standardized company names

**Flow**:
```
Query → Clean Text → Multiple Matching Strategies → Company Name
```

**Matching Strategies** (in order):
1. **Exact Match**: Query exactly matches company name
2. **Token Match**: Query contains company name tokens
3. **Substring Match**: Company name is substring of query
4. **Fuzzy Match**: SequenceMatcher ratio > 0.7
5. **spaCy NER**: Extract ORG entities and match
6. **Capitalization Fallback**: Find capitalized words

**Key Functions**:
- `load_sp500()` - Load company database from CSV
- `normalize_text()` - Normalize unicode and spaces
- `clean_text()` - Remove special characters
- `extract_company_name()` - Main extraction logic

**Example**:
```python
extract_company_name("Tell me about Apple Inc")
# Returns: "Apple Inc"

extract_company_name("MSFT stock performance")
# Returns: "Microsoft Corporation"
```

### 2. News Fetcher (`backend/news_fetcher.py`)

**Purpose**: Fetch and extract news articles about companies

**Flow**:
```
Company → BBC Search → Extract Links → Fetch Articles → Return Text
```

**Key Functions**:
- `get_bbc_news_content()` - Search BBC News
- `extract_hrefs()` - Extract article links from search results
- `extract_paragraphs()` - Extract and clean article content
- `get_news_content()` - Main orchestration function

**Features**:
- User-Agent headers to avoid blocking
- Timeout handling (10 seconds)
- Error recovery
- Duplicate removal
- Content validation (minimum 50 chars)

**Example**:
```python
news = get_news_content("Apple")
# Returns: List of 3-5 article texts

print(f"Found {len(news)} articles")
print(news[0][:200])  # First 200 chars of first article
```

### 3. Stock Info Formatter (`backend/stock_info_formatter.py`)

**Purpose**: Fetch and organize financial data

**Flow**:
```
Ticker → yfinance → Extract Metrics → Organize by Category → Return Dict
```

**Data Categories**:
- Company Info (name, ticker, sector, industry, website)
- Location (address, city, state, country)
- Market Data (price, volume, changes)
- Valuation Metrics (P/E, P/B, beta)
- Financials (revenue, cash flow, growth)
- Dividends & Splits
- Analyst Targets

**Key Functions**:
- `get_stock_info()` - Fetch and return structured data
- `print_stock_info()` - Display formatted output

**Example**:
```python
stock = get_stock_info("AAPL")
# Returns: {
#   "Company Info": {"symbol": "AAPL", "longName": "Apple Inc", ...},
#   "Market Data": {"currentPrice": 150.25, ...},
#   ...
# }

print(stock["Market Data"]["currentPrice"])  # 150.25
```

### 4. Pipeline Orchestrator (`pipeline.py`)

**Purpose**: Coordinate all components and generate final report

**Main Functions**:

#### `load_summarizer()`
- Loads BART summarization model
- ~1.6GB, loaded on first run only
- Handles loading errors gracefully

#### `safe_summarize(text, max_chars=1500)`
- Safely summarizes text
- Adapts summary length based on input
- Catches and logs errors

#### `chunk_text(text, max_chars=1500)`
- Splits long text into chunks
- Prevents token limit exceeded errors
- Maintains word boundaries

#### `fetch_news(company_name)`
- Orchestrates news fetching and summarization
- Logs progress
- Returns list of summaries

#### `fetch_stock_info(company_name)`
- Fetches stock data via yfinance
- Handles ticker lookup
- Extracts key metrics

#### `aggregate_information()`
- Combines all data into structured format
- Adds timestamp
- Returns JSON-ready dict

#### `generate_detailed_report()`
- Calls OpenRouter API with aggregated data
- Constructs professional prompt
- Returns formatted report text

#### `run_pipeline(query)`
- Main orchestration function
- Coordinates all components
- Saves results to file

**Flow Diagram**:
```
run_pipeline(query)
    ├─ extract_company_name(query)
    ├─ fetch_news(company)
    ├─ fetch_stock_info(company)
    ├─ aggregate_information()
    ├─ generate_detailed_report()
    ├─ Display report
    └─ Save to file
```

## Data Flow

### Step-by-Step Execution

```
1. USER INPUT
   Input: "Tell me about Tesla"
   
2. COMPANY EXTRACTION
   Process: extract_company_name("Tell me about Tesla")
   Output: "Tesla Inc"
   
3. PARALLEL DATA COLLECTION
   3a. NEWS FETCHING:
       - Search BBC: "https://bbc.com/search?q=Tesla+Inc"
       - Extract links from search results
       - Fetch 5 articles
       - Extract paragraph text
       
   3b. STOCK DATA:
       - Query yfinance: Ticker("TSLA")
       - Extract 20+ financial metrics
       - Organize by category
       
4. SUMMARIZATION (on news)
   - Split articles into chunks (1500 chars max)
   - Summarize each chunk with BART
   - Combine summaries
   - Generate final summary
   
5. AGGREGATION
   Create report object:
   {
     "company_name": "Tesla Inc",
     "stock_information": {...},
     "news_summaries": [...],
     "timestamp": "2025-11-23T10:30:00"
   }
   
6. AI ANALYSIS
   - Create prompt with all data
   - Call OpenRouter API (Grok 4.1 model)
   - Receive detailed analysis
   - Format with sections
   
7. OUTPUT
   - Display on console
   - Save to file: report_Tesla_Inc_2025-11-23.txt
   - Show completion message
```

## Error Handling Strategy

### Component-Level Errors

```
Try to extract company
  ├─ Success → Continue
  └─ Fail → Log error, ask user to try again

Try to fetch news
  ├─ Success → Continue
  └─ Fail → Log warning, continue with empty news list

Try to fetch stock info
  ├─ Success → Continue
  └─ Fail → Log warning, continue with None values

Try to summarize
  ├─ Success → Continue
  └─ Fail → Log error, use original text

Try to generate report
  ├─ Success → Save and display
  └─ Fail → Show error message to user
```

### User-Facing Error Messages

```
[ERROR] Could not extract company name from query.
  → User should try: "Apple Inc", "Microsoft", "Tesla"

[WARNING] Could not fetch stock info for {company}
  → Continue with available data, show what's missing

[NEWS] No articles found.
  → Check internet or try different company

[ERROR] Error generating detailed report: {error}
  → Check API key, internet, or rate limits
```

## Integration Points

### External Dependencies

| Component | Library | Purpose | Usage |
|-----------|---------|---------|-------|
| Extraction | spacy | NER, tokenization | Company name extraction |
| Extraction | pandas | Data processing | Load S&P 500 CSV |
| Extraction | difflib | Fuzzy matching | Similarity scoring |
| News | feedparser | RSS/Atom parsing | Parse news feeds |
| News | newspaper3k | Article extraction | Extract article content |
| News | requests | HTTP requests | Fetch URLs |
| News | BeautifulSoup | HTML parsing | Parse HTML |
| Stock | yfinance | Financial data | Fetch stock metrics |
| Summarization | transformers | ML models | Load BART model |
| Summarization | torch | Deep learning | Model inference |
| API | openai | LLM access | Call Grok model |

### API Keys Required

```python
# OpenRouter API
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key="sk-or-v1-..."  # Required: Get from https://openrouter.ai
)
```

## Configuration & Customization

### Easy Customizations

**Change news article count**:
```python
# In pipeline.py, line 80
contents = contents[:3]  # Instead of [:5]
```

**Change LLM model**:
```python
# In pipeline.py, line 148
model="openai/gpt-4-turbo",  # Instead of x-ai/grok-4.1-fast
```

**Change summarization length**:
```python
# In pipeline.py, lines 45-52
if token_len < 80:
    max_len = 30  # Shorter summaries
```

### Advanced Customizations

**Add different news source**:
```python
# Modify backend/news_fetcher.py
def get_reuters_news(topic):
    # Fetch from Reuters instead of BBC
    pass
```

**Add sentiment analysis**:
```python
# Add to pipeline.py
from textblob import TextBlob

def analyze_sentiment(articles):
    return [TextBlob(a).sentiment.polarity for a in articles]
```

**Add caching**:
```python
import pickle

def cache_stock_data(ticker, data):
    with open(f"cache_{ticker}.pkl", "wb") as f:
        pickle.dump(data, f)
```

## Performance Metrics

| Component | Time | Notes |
|-----------|------|-------|
| Company extraction | < 100ms | Very fast |
| News fetching | 5-15s | Network dependent |
| News summarization | 30-60s | BART model slow on CPU |
| Stock info fetch | 1-3s | Fast API |
| Report generation | 10-30s | API dependent |
| Total pipeline | 2-5 min | First run slower (model load) |

## Testing Strategy

### Unit Tests
```python
# Test each component independently
test_company_extraction()
test_stock_info()
test_news_fetching()
```

### Integration Tests
```python
# Test components together
test_pipeline_components()

# Test with real data
run_pipeline("Apple")
```

### Edge Cases
- Company not in database
- No news articles available
- Invalid ticker
- API rate limits
- Network timeouts

## Deployment Considerations

### Requirements
- Python 3.8+
- 2GB RAM (for BART model)
- Internet connection
- Valid OpenRouter API key

### Scalability
- Single company: Works fine
- Multiple companies: Can parallelize
- Batch processing: Implement queue system
- Production: Add database, caching, logging

### Security
- API keys stored in environment variables
- Input validation on queries
- Rate limiting on API calls
- Error messages don't expose sensitive data

## Monitoring & Logging

### Current Logging
```python
print("[STEP 1] Extracting company name...")
print("[SUCCESS] Detected company: Apple Inc")
print("[ERROR] Could not extract company...")
```

### Recommended Enhancements
```python
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

logger.info("Processing company: Apple")
logger.warning("No news articles found")
logger.error("API error: Rate limit exceeded")
```

## Future Enhancements Roadmap

### Phase 1: Quality
- [ ] Add more news sources
- [ ] Implement sentiment analysis
- [ ] Add error recovery/retry logic
- [ ] Create logging system

### Phase 2: Performance
- [ ] Cache stock data (24h)
- [ ] Parallel processing
- [ ] GPU support for BART
- [ ] Asynchronous API calls

### Phase 3: Features
- [ ] Competitor analysis
- [ ] Historical trends
- [ ] Earnings predictions
- [ ] ESG scoring

### Phase 4: Deployment
- [ ] Web UI/Dashboard
- [ ] Database backend
- [ ] Scheduled reports
- [ ] Email delivery
- [ ] API endpoint

## Summary

The pipeline is designed as a modular, extensible system that:
1. **Extracts** company names from user input
2. **Fetches** data from multiple sources (news, stock market)
3. **Processes** data through summarization and formatting
4. **Aggregates** information into structured format
5. **Analyzes** with AI to create insights
6. **Outputs** professional reports

Each component is independent and can be:
- Tested separately
- Modified independently
- Replaced with alternatives
- Extended with new features
