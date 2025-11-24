# Pipeline Usage Guide

## Quick Start

### 1. Basic Usage

Run the main pipeline:
```bash
python pipeline.py
```

Example interaction:
```
Enter a company name or topic: Apple

================================================================================
FINANCIAL INTELLIGENCE PIPELINE
================================================================================

[STEP 1] Extracting company name from query: 'Apple'
[SUCCESS] Detected company: Apple Inc

[FETCHING NEWS] Searching for news about Apple Inc...
[NEWS] Found 3 articles. Summarizing...
  - Summarizing article 1/3...
  - Summarizing article 2/3...
  - Summarizing article 3/3...
[NEWS] Found 3 articles. Summarizing...

[FETCHING STOCK INFO] Retrieving stock data for Apple Inc...
[STOCK] Stock data retrieved successfully.

[AGGREGATING] Combining all information...

[GENERATING REPORT] Creating detailed analysis with AI...
[REPORT] Detailed report generated successfully.

================================================================================
DETAILED ANALYSIS REPORT
================================================================================

[Comprehensive AI-generated report appears here]

================================================================================

[SAVED] Report saved to: report_Apple_Inc_2025-11-23.txt
```

### 2. Test Individual Components

To test components without full report generation:

```bash
python test_pipeline.py
```

This runs:
- Company name extraction tests
- Stock information fetching tests
- News fetching tests
- Full pipeline component test

### 3. Use in Your Own Code

Import and use the pipeline components:

```python
from pipeline import run_pipeline

# Run the full pipeline
run_pipeline("Tesla")
```

Or use individual components:

```python
from backend.extract_company_name import extract_company_name
from backend.news_fetcher import get_news_content
from backend.stock_info_formatter import get_stock_info

# Extract company
company = extract_company_name("Tell me about Microsoft")
print(f"Company: {company}")

# Get news
news = get_news_content(company)
print(f"Articles: {len(news)}")

# Get stock info
stock = get_stock_info("MSFT")
print(f"Stock Price: {stock['Market Data']['currentPrice']}")
```

## Pipeline Flow

```
┌─────────────────────────────┐
│   User Input (Query)        │
│  "Tell me about Apple"      │
└──────────────┬──────────────┘
               │
               ▼
┌─────────────────────────────┐
│  Extract Company Name       │
│  Input: Natural language    │
│  Output: "Apple Inc"        │
└──────────────┬──────────────┘
               │
       ┌───────┴───────┐
       │               │
       ▼               ▼
   ┌────────────┐  ┌──────────────────┐
   │ Fetch News │  │ Fetch Stock Info │
   │  Articles  │  │   via yfinance   │
   └──────┬─────┘  └────────┬─────────┘
          │                 │
          ▼                 ▼
    ┌──────────────┐  ┌─────────────┐
    │ Summarize    │  │ Format Data │
    │ with BART    │  │  for Report │
    └──────┬───────┘  └─────┬───────┘
           │                │
           └────────┬───────┘
                    │
                    ▼
          ┌─────────────────────┐
          │ Aggregate Info      │
          │ Create JSON Report  │
          └─────────────────────┘
                    │
                    ▼
          ┌─────────────────────┐
          │ Generate Report     │
          │ via OpenRouter API  │
          │ (Grok Model)        │
          └──────────┬──────────┘
                     │
                     ▼
          ┌─────────────────────┐
          │ Save to File        │
          │ Display Results     │
          └─────────────────────┘
```

## Output Files

The pipeline creates report files named: `report_<COMPANY>_<DATE>.txt`

Example: `report_Apple_Inc_2025-11-23.txt`

Report contains:
1. Stock Information section
2. Recent News Summaries section
3. Detailed AI Analysis section

## Configuration

### Change API Key

Edit `pipeline.py`, line ~145:
```python
api_key="your-new-api-key-here",
```

Get a free API key from: https://openrouter.ai

### Change LLM Model

Edit `pipeline.py`, line ~148:
```python
model="x-ai/grok-4.1-fast",  # Change this
```

Available models:
- `x-ai/grok-4.1-fast` - Fast (default)
- `openai/gpt-4-turbo` - Powerful
- `anthropic/claude-3-sonnet` - Balanced

### Adjust News Article Count

Edit `pipeline.py`, line ~80:
```python
contents = contents[:5]  # Change 5 to desired count
```

### Change Summary Length

Edit `pipeline.py`, lines ~45-52:
```python
if token_len < 80:
    max_len = 50      # Change these values
elif token_len < 200:
    max_len = 100
else:
    max_len = 250
```

## Troubleshooting

### Issue: "No company detected"
**Solution**: Try being more specific
- Bad: "tech company"
- Good: "Apple Inc" or "Microsoft"

### Issue: "No articles found"
**Solutions**:
- Check internet connection
- Try a more popular company
- BBC News might be slow

### Issue: Summarizer takes too long
**Solution**: First run loads the model (~2 min). Subsequent runs are faster.

### Issue: "API rate limit exceeded"
**Solution**: 
- Wait 5 minutes
- Upgrade your OpenRouter plan
- Use a different API key

### Issue: Stock data shows "N/A"
**Solutions**:
- Check ticker symbol is correct
- Market might be closed
- Company might be delisted

## Advanced Usage

### Custom Report Prompt

Edit `pipeline.py`, function `generate_detailed_report()`:

```python
prompt = f"""
Your custom prompt here.
Use {company_name} for company
Use {stock_info} for stock data
Use {news} for news summaries
"""
```

### Use Different News Source

Edit `backend/news_fetcher.py`:

Replace BBC search with:
- Google News
- Reuters
- Bloomberg
- Financial Times

### Add Data Caching

Modify `pipeline.py` to cache:
- Stock data (update daily)
- News summaries (update weekly)
- Reports (archive old ones)

### Batch Processing

Process multiple companies:

```python
companies = ["Apple", "Microsoft", "Google", "Amazon", "Tesla"]

for company in companies:
    print(f"\nProcessing {company}...")
    run_pipeline(company)
    print(f"Completed {company}!\n")
```

## Performance Tips

1. **Faster News Fetching**: Limit to 3 articles instead of 5
2. **Skip Summarization**: Comment out summarizer in `fetch_news()`
3. **Cache Results**: Save previous reports, reuse stock data
4. **Parallel Processing**: Use threading for news + stock fetching
5. **Offline Mode**: Pre-download company data

## API Costs

- **OpenRouter**: ~$0.001-$0.01 per report (depending on model)
- **yfinance**: Free
- **BBC News**: Free
- Total per report: < $0.02

## Best Practices

1. ✓ Start with well-known companies
2. ✓ Check internet connection before running
3. ✓ Save important reports to backup
4. ✓ Use specific company names (not abbreviations)
5. ✓ Run during market hours for stock data
6. ✓ Monitor API key usage to avoid overages
7. ✓ Test components individually first

## Next Steps

1. Run `python pipeline.py` to test
2. Enter a company name (e.g., "Apple", "Tesla")
3. Wait for report generation (2-5 minutes)
4. Review generated report
5. Customize as needed

## Support Resources

- **Company List**: `datasets/companies.csv`
- **Documentation**: `PIPELINE_README.md`
- **Test Script**: `test_pipeline.py`
- **API Docs**: https://openrouter.ai/docs
- **yfinance**: https://github.com/ranaroussi/yfinance
