# Quick Reference Card

## Files & Functions

### Core Pipeline
| File | Function | Input | Output |
|------|----------|-------|--------|
| `pipeline.py` | `run_pipeline(query)` | User query string | Generates report |
| `pipeline.py` | `load_summarizer()` | None | BART model |
| `pipeline.py` | `safe_summarize(text)` | Article text | Summary text |

### Company Extraction
| File | Function | Input | Output |
|------|----------|-------|--------|
| `backend/extract_company_name.py` | `extract_company_name(query)` | User query | Company name |
| `backend/extract_company_name.py` | `load_sp500()` | None | Company set |
| `backend/extract_company_name.py` | `normalize_text(s)` | Text | Normalized |
| `backend/extract_company_name.py` | `clean_text(s)` | Text | Cleaned |

### News Fetching
| File | Function | Input | Output |
|------|----------|-------|--------|
| `backend/news_fetcher.py` | `get_news_content(topic)` | Company name | List of articles |
| `backend/news_fetcher.py` | `get_bbc_news_content(topic)` | Topic | Search URL |
| `backend/news_fetcher.py` | `extract_hrefs(url)` | URL | Article links |
| `backend/news_fetcher.py` | `extract_paragraphs(url)` | URL | Article text |

### Stock Information
| File | Function | Input | Output |
|------|----------|-------|--------|
| `backend/stock_info_formatter.py` | `get_stock_info(ticker)` | Ticker | Stock dict |
| `backend/stock_info_formatter.py` | `print_stock_info(ticker)` | Ticker | Prints formatted |

## Command Reference

```bash
# Run full pipeline
python pipeline.py

# Test components
python test_pipeline.py

# Test extraction only
python -c "from backend.extract_company_name import extract_company_name; \
  print(extract_company_name('Apple'))"

# Test stock info
python -c "from backend.stock_info_formatter import get_stock_info; \
  info = get_stock_info('AAPL'); print(info.keys())"

# Test news fetching
python -c "from backend.news_fetcher import get_news_content; \
  news = get_news_content('Apple'); print(f'Found {len(news)} articles')"
```

## Configuration Quick Changes

### API Key (line 145 in pipeline.py)
```python
api_key="sk-or-v1-YOUR-KEY-HERE"
```

### LLM Model (line 148 in pipeline.py)
```python
model="x-ai/grok-4.1-fast"  # Change this
# Options: openai/gpt-4-turbo, anthropic/claude-3-sonnet
```

### News Count (line 80 in pipeline.py)
```python
contents = contents[:5]  # Change 5 to your preference
```

### Summary Length (lines 45-52 in pipeline.py)
```python
if token_len < 80:
    max_len = 50      # Shorter = faster, longer = more detail
elif token_len < 200:
    max_len = 100
else:
    max_len = 250
```

## Data Files

| File | Purpose | Format | Location |
|------|---------|--------|----------|
| `companies.csv` | S&P 500 list | CSV | `datasets/` |
| `report_*.txt` | Generated reports | Text | Project root |
| `requirements.txt` | Python packages | Text | Project root |

## Variables & Constants

```python
# In extract_company_name.py
ALL_COMPANIES  # Set of all company names (loaded from CSV)
GARBAGE        # Set of words to ignore in extraction

# In news_fetcher.py
max_chars=1500     # News chunk size
timeout=10         # Request timeout in seconds

# In pipeline.py
max_chars=1500     # Text chunk size
max_results=5      # Number of articles to process
do_sample=False    # BART: deterministic summarization

# Stock data sections:
"Company Info"
"Location"
"Market Data"
"Valuation Metrics"
"Financials"
"Dividends & Splits"
"Analyst Targets"
```

## Common Issues & Solutions

| Issue | Cause | Solution |
|-------|-------|----------|
| "No company detected" | Query too vague | Use specific names |
| "No articles found" | BBC unavailable | Check internet |
| Slow summarization | First run | Wait 1-2 min, next runs faster |
| API rate limit | Too many calls | Wait 5 minutes |
| Stock data "N/A" | Invalid ticker | Check company exists |
| Import errors | Missing package | Run `pip install -r requirements.txt` |

## Key Dependencies

```python
# ML & NLP
transformers  # BART summarization
torch         # Deep learning
spacy         # NLP, NER
nltk          # Natural language toolkit

# Data & Web
pandas        # Data processing
requests      # HTTP requests
beautifulsoup4  # HTML parsing
feedparser    # RSS parsing

# Finance
yfinance      # Stock data
alpha_vantage # Stock data alternative

# LLM & API
openai        # LLM access (OpenRouter compatible)

# Utilities
numpy         # Numerical operations
```

## File Structure

```
Project/
├── pipeline.py                    ⭐ Main entry point
├── main.py                        Original version
├── test_pipeline.py               Testing
├── test2deepseek.py               API test
├── requirements.txt               Dependencies
├── PIPELINE_README.md             📖 Full documentation
├── USAGE_GUIDE.md                📖 How to use
├── ARCHITECTURE.md               📖 Technical details
├── QUICK_REFERENCE.md            📖 This file
├── backend/
│   ├── extract_company_name.py   Extract company names
│   ├── news_fetcher.py           Fetch BBC news
│   └── stock_info_formatter.py   Get stock data
├── datasets/
│   └── companies.csv             S&P 500 list
└── frontend/
    └── (empty)
```

## Quick Start (30 seconds)

1. Open terminal in project folder
2. Run: `python pipeline.py`
3. Enter: `Apple`
4. Wait 2-5 minutes
5. Read report in console and saved file

## Full Query Examples

```
python pipeline.py
Enter a company name or topic: Apple Inc
→ Generates report about Apple

python pipeline.py
Enter a company name or topic: Tell me about Microsoft
→ Extracts "Microsoft" and generates report

python pipeline.py
Enter a company name or topic: Show me Tesla stock
→ Extracts "Tesla" and generates report
```

## Performance Baseline

| Operation | Time | Note |
|-----------|------|------|
| Company extraction | < 0.1s | Very fast |
| News fetch (3 articles) | 10-15s | Network I/O |
| Stock data fetch | 1-3s | API call |
| News summarization (3x) | 30-60s | BART inference |
| Report generation | 10-30s | LLM API call |
| **Total first run** | **2-5 min** | Includes model load |
| **Total subsequent** | **1-3 min** | Model cached |

## Customization Templates

### Add new data source:
```python
def get_data_from_SOURCE(topic):
    # Fetch data
    # Process
    # Return formatted
    return data

# Call in pipeline.py: run_pipeline()
```

### Modify prompt:
```python
# In generate_detailed_report()
prompt = f"""
New instructions here.
Use {company_name}, {stock_info}, {news}
"""
```

### Add post-processing:
```python
def post_process_report(report):
    # Enhance report
    return enhanced_report

# Call after generate_detailed_report()
```

## API & Libraries

| Purpose | Library | Method | Example |
|---------|---------|--------|---------|
| Company extraction | spacy | nlp.pipe() | `nlp(text).ents` |
| Matching | difflib | SequenceMatcher | `ratio()` |
| CSV loading | pandas | read_csv() | `pd.read_csv()` |
| HTML parsing | BeautifulSoup | find_all() | `soup.find_all('p')` |
| News search | BBC | HTTP GET | `requests.get(url)` |
| Stock data | yfinance | Ticker() | `yf.Ticker('AAPL')` |
| Summarization | transformers | pipeline() | `pipeline('summarization')` |
| LLM API | OpenRouter | chat.completions | `client.chat.completions.create()` |

## Debugging Tips

```python
# Add debug prints
print(f"[DEBUG] company = {company}")
print(f"[DEBUG] stock_info keys = {stock_info.keys()}")
print(f"[DEBUG] news_count = {len(news_summaries)}")

# Test component individually
from backend.extract_company_name import extract_company_name
result = extract_company_name("Test query")
print(f"Result: {result}")

# Catch exceptions
try:
    run_pipeline("Apple")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
```

## Environment Info

- Python: 3.8+ (tested with 3.12)
- OS: Windows/Linux/Mac
- RAM: 2GB+ (for BART)
- Disk: ~2GB (for models)
- Internet: Required

## Getting Help

1. Read `PIPELINE_README.md` - Full documentation
2. Read `ARCHITECTURE.md` - Technical design
3. Read `USAGE_GUIDE.md` - How to use
4. Run `test_pipeline.py` - Test components
5. Check error messages - Usually clear
6. Check API key - Most common issue
7. Check internet - Second most common
