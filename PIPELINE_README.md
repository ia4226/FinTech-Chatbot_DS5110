# Financial Intelligence Pipeline

## Overview

This pipeline integrates multiple components to provide comprehensive financial intelligence on companies:

1. **Company Name Extraction** - Extracts company names from natural language queries
2. **News Fetching** - Retrieves recent news articles about the company
3. **Stock Information** - Fetches real-time stock data and financial metrics
4. **News Summarization** - Uses AI to summarize long articles
5. **Detailed Report Generation** - Creates comprehensive analysis using OpenAI/Grok API

## Architecture

```
User Input (Query)
    ↓
Extract Company Name
    ↓
├── Fetch News Articles
│   └── Summarize with BART
├── Fetch Stock Information
│   └── Process via yfinance
└── Aggregate Information
    ↓
Generate Detailed Report (OpenAI)
    ↓
Output Report (Console + File)
```

## Components

### 1. `extract_company_name.py`
Extracts company names from user queries using:
- Exact matching against S&P 500 list
- Token-based matching
- Fuzzy matching (SequenceMatcher)
- spaCy NER (Named Entity Recognition)
- Fallback capitalization detection

**Input**: Any user query (e.g., "Tell me about Apple")
**Output**: Company name (e.g., "Apple Inc.")

### 2. `news_fetcher.py`
Fetches news articles about the company:
- Searches BBC News
- Extracts article links
- Fetches and cleans article content
- Implements error handling and timeouts

**Input**: Company name
**Output**: List of article texts (up to 5 articles)

### 3. `stock_info_formatter.py`
Fetches stock and financial information:
- Company information (name, ticker, sector, industry)
- Current market data (price, market cap, etc.)
- Valuation metrics (P/E ratio, price-to-book, etc.)
- Financial data (revenue, cash flow, etc.)
- Dividend information

**Input**: Company ticker or name
**Output**: Dictionary of stock information

### 4. `pipeline.py`
Main orchestration script that:
- Loads the BART summarization model
- Chains all components together
- Aggregates information
- Generates detailed reports
- Saves results to file

## Installation

1. Install required dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `transformers` - For BART summarization
- `torch` - PyTorch (required by transformers)
- `spacy` - NLP for company extraction
- `pandas` - Data processing
- `bs4` - HTML parsing
- `feedparser` - RSS feed parsing
- `newspaper3k` - Article extraction
- `yfinance` - Stock data
- `openai` - LLM API access
- `requests` - HTTP requests

2. Download spaCy model:
```bash
python -m spacy download en_core_web_sm
```

3. Set up OpenAI/OpenRouter API key:
   - Update the API key in `pipeline.py` (line with `api_key=...`)
   - Get API key from: https://openrouter.ai

## Usage

### Quick Start

```bash
python pipeline.py
```

Then enter a company name or query:
```
Enter a company name or topic: Apple
```

### Expected Output

The pipeline will:
1. Extract company name: "Apple Inc."
2. Fetch and summarize recent news
3. Fetch stock information
4. Generate detailed analysis report
5. Save report to file: `report_Apple_Inc_YYYY-MM-DD.txt`

### Example Report Sections

- **Company Overview** - Brief description
- **Stock Performance Analysis** - Price, metrics, valuation
- **Market Position** - Industry and sector analysis
- **Recent Events** - Summary of news
- **Key Insights & Recommendations** - Analysis and outlook
- **Risk Factors** - Potential risks

## Configuration

### Modify News Fetcher
Edit `backend/news_fetcher.py`:
- Change `get_bbc_news_content()` to use different news sources
- Adjust article count in `get_news_content()` function

### Modify Stock Data
Edit `backend/stock_info_formatter.py`:
- Add/remove stock fields in the `sections` dictionary
- Customize field extraction

### Modify Report Generation
Edit `pipeline.py`:
- Adjust `safe_summarize()` for different summary lengths
- Modify `generate_detailed_report()` prompt for different analysis
- Change LLM model (currently: `x-ai/grok-4.1-fast`)

## Error Handling

The pipeline includes robust error handling for:
- Missing company names
- Network timeouts
- Invalid stock tickers
- API failures
- Missing data fields

Errors are logged with clear messages, and the pipeline attempts to continue with available data.

## Performance

- **Speed**: 2-5 minutes per report (depends on network and API response times)
- **Model Loading**: BART model (~1.6GB) loads on first run
- **API Calls**: 
  - 1x OpenRouter API call for final report
  - Multiple requests to BBC News and yfinance

## Troubleshooting

### No news articles found
- Check internet connection
- Company name might be too obscure
- BBC News website structure might have changed

### Stock info unavailable
- Invalid company ticker
- Market closed (try the next trading day)
- Company might be delisted

### Summarization too slow
- First run loads 1.6GB model (wait 1-2 minutes)
- Subsequent runs are faster
- Can disable summarization by modifying `pipeline.py`

### API rate limits
- OpenRouter has rate limits
- Wait a few minutes before next request
- Consider upgrading API plan

## Data Sources

1. **Company Names**: `datasets/companies.csv` (S&P 500)
2. **News**: BBC News (https://www.bbc.com)
3. **Stock Data**: Yahoo Finance via yfinance
4. **Analysis**: OpenRouter API (Grok model)

## Project Structure

```
Project/
├── pipeline.py                      # Main orchestration
├── main.py                          # Original simple demo
├── test2deepseek.py                 # API test script
├── requirements.txt                 # Python dependencies
├── datasets/
│   └── companies.csv               # S&P 500 companies
└── backend/
    ├── extract_company_name.py     # Company extraction
    ├── news_fetcher.py             # News fetching
    └── stock_info_formatter.py     # Stock data formatting
```

## Future Enhancements

1. Multi-source news fetching (Reuters, Bloomberg, etc.)
2. Sentiment analysis on news articles
3. Historical stock price analysis
4. Competitor analysis
5. Earnings predictions
6. ESG scoring
7. Web UI/Dashboard
8. Database for caching reports
9. Scheduled report generation
10. Email delivery of reports

## License

This project is for educational purposes.

## Support

For issues or questions, please refer to the error messages and troubleshooting section above.
