import json
from src.modules.extract_company_name import extract_company_name
from src.modules.news_fetcher import get_news_content
from src.modules.stock_info_formatter import get_stock_info
from openai import OpenAI
import os
import yfinance as yf
import sys
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (.env must be in project root)
load_dotenv()

# Fetch API key and base URL from environment
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

# Initialize summarizer
def load_summarizer():
    """Load the summarization model."""
    # Deprecated: summarization now uses the OpenAI/Grok API.
    # Keep this function for compatibility but return None.
    return None

def get_openai_client():
    """Return an OpenAI client configured with hardcoded API key (temporary).

    Returns None when no API key is available.
    """
    api_key = OPENROUTER_API_KEY
    if not api_key:
        return None
    base_url = OPENAI_BASE_URL
    return OpenAI(base_url=base_url, api_key=api_key)

def summarize_with_grok(text: str, company_name: str | None = None) -> str:
    """Summarize `text` using the Grok model via the OpenAI client.

    Returns a summary string with detailed bullet points. On failure returns an explanatory message.
    """
    try:
        client = get_openai_client()
        if client is None:
            return "[Summary unavailable: OPENAI_API_KEY not set]"

        # Ask Grok to produce longer, more detailed summaries with proper structure
        prompt_company = f" about {company_name}" if company_name else ""
        prompt = (
            f"You are a professional news summarizer. Summarize the following news article{prompt_company}"
            " in 4-6 detailed bullet points (300-400 words total). Focus on key facts, developments, and impact."
            " Use proper bullet formatting with clear line breaks between points. Keep it factual and neutral.\n\n"
            f"ARTICLE:\n{text}"
        )

        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=800,
        )

        content = getattr(response.choices[0].message, 'content', None)
        return content if isinstance(content, str) and content.strip() else "[No summary returned]"
    except Exception as e:
        return f"[Summary failed: {e}]"

def safe_summarize(summarizer, text, max_chars=1500):
    """Safely summarize text with dynamic length adjustment."""
    try:
        if not text or len(text.strip()) < 50:
            return text

        # Use Grok-based summarizer instead of local transformers model.
        # `summarizer` param is ignored for backwards compatibility.
        return summarize_with_grok(text)
    except Exception as e:
        return f"[Summary failed: {e}]"

def chunk_text(text, max_chars=1500):
    """Split text into chunks for summarization."""
    chunks = []
    words = text.split()
    current = []

    for w in words:
        if sum(len(x) for x in current) + len(w) + len(current) > max_chars:
            chunks.append(" ".join(current))
            current = []
        current.append(w)


    if current:
        chunks.append(" ".join(current))

    return chunks

def fetch_news(company_name):
    """Fetch and summarize news articles about the company."""
    print(f"\n[FETCHING NEWS] Searching for news about {company_name}...")
    try:
        contents = get_news_content(company_name)
        
        if not contents:
            print("[NEWS] No articles found.")
            return []
        # Prefer articles that explicitly mention the company name (case-insensitive)
        company_lower = (company_name or "").lower()
        filtered = [c for c in contents if c and company_lower in c.lower()]

        if filtered:
            selected = filtered[:5]
            print(f"[NEWS] Found {len(filtered)} company-specific articles; summarizing top {len(selected)}...")
        else:
            # Fallback: use the first few articles returned by the fetcher
            selected = contents[:5]
            print(f"[NEWS] No explicit company mentions found; summarizing top {len(selected)} returned articles...")

        summaries = []
        for idx, article_text in enumerate(selected, start=1):
            print(f"  - Summarizing article {idx}/{len(selected)}...")
            chunks = chunk_text(article_text)
            partial = []

            for c in chunks:
                summary = safe_summarize(None, c)
                partial.append(summary)

            combined = " ".join([p for p in partial if p])
            if len(combined) > 100:
                final_summary = safe_summarize(None, combined)
            else:
                final_summary = combined

            summaries.append(final_summary)

        return summaries
    except Exception as e:
        print(f"[ERROR] Error fetching news: {e}")
        return []


def fetch_stock_info(company_name):
    print(f"[FETCHING STOCK INFO] Query received: {company_name}")

    # Step 1: Ask LLM for ticker
    ticker = get_stock_ticker(company_name)

    # Step 2: Validate
    if not ticker or ticker == "NONE" or len(ticker) > 5:
        print("[WARNING] LLM ticker seems invalid. Falling back to YFinance search.")
        ticker = company_name

    print(f"[INFO] Using ticker: {ticker}")

    try:
        yf_obj = yf.Ticker(ticker)
        info = yf_obj.info

        if not info or not info.get("symbol"):
            print(f"[WARNING] YFinance could not fetch info for {ticker}")
            return None

        stock_data = {
            "ticker": info.get('symbol', 'N/A'),
            "longName": info.get('longName', 'N/A'),
            "sector": info.get('sector', 'N/A'),
            "industry": info.get('industry', 'N/A'),
            "currentPrice": info.get('currentPrice', 'N/A'),
            "marketCap": info.get('marketCap', 'N/A'),
            "trailingPE": info.get('trailingPE', 'N/A'),
            "dividendYield": info.get('dividendYield', 'N/A'),
            "52WeekHigh": info.get('fiftyTwoWeekHigh', 'N/A'),
            "52WeekLow": info.get('fiftyTwoWeekLow', 'N/A'),
            "totalRevenue": info.get('totalRevenue', 'N/A'),
            "freeCashflow": info.get('freeCashflow', 'N/A'),
            "website": info.get('website', 'N/A'),
        }

        print("[STOCK] Data retrieved successfully.")
        return stock_data

    except Exception as e:
        print(f"[ERROR] {e}")
        return None


# def fetch_stock_info(company_name):
#     """Fetch stock information for the company."""
#     company_name = get_stock_ticker(company_name)
#     print(f"\n[FETCHING STOCK INFO] Retrieving stock data for {company_name}...")
#     try:
#         # Try to get ticker from yfinance
#         ticker_search = yf.Ticker(company_name)
#         if not ticker_search.info or not ticker_search.info.get('symbol'):
#             # Try company name as is
#             ticker = company_name
#         else:
#             ticker = ticker_search.info.get('symbol', company_name)
        
#         t = yf.Ticker(ticker)
#         info = t.info
        
#         if not info or info.get('symbol') is None:
#             print(f"[WARNING] Could not fetch stock info for {company_name}")
#             return None
        
#         # Extract key information
#         stock_data = {
#             "ticker": info.get('symbol', 'N/A'),
#             "longName": info.get('longName', 'N/A'),
#             "sector": info.get('sector', 'N/A'),
#             "industry": info.get('industry', 'N/A'),
#             "currentPrice": info.get('currentPrice', 'N/A'),
#             "marketCap": info.get('marketCap', 'N/A'),
#             "trailingPE": info.get('trailingPE', 'N/A'),
#             "dividendYield": info.get('dividendYield', 'N/A'),
#             "52WeekHigh": info.get('fiftyTwoWeekHigh', 'N/A'),
#             "52WeekLow": info.get('fiftyTwoWeekLow', 'N/A'),
#             "totalRevenue": info.get('totalRevenue', 'N/A'),
#             "freeCashflow": info.get('freeCashflow', 'N/A'),
#             "website": info.get('website', 'N/A'),
#         }
        
#         print("[STOCK] Stock data retrieved successfully.")
#         return stock_data
#     except Exception as e:
#         print(f"[ERROR] Error fetching stock info: {e}")
#         return None

def aggregate_information(company_name, news_summaries, stock_info):
    """Aggregate all information into a structured report."""
    print("\n[AGGREGATING] Combining all information...")
    
    report = {
        "company_name": company_name,
        "stock_information": stock_info,
        "news_summaries": news_summaries,
        "timestamp": datetime.now().isoformat()
    }
    
    return report

def generate_detailed_report(company_name, report):
    """Generate a detailed report using OpenAI API."""
    print("\n[GENERATING REPORT] Creating detailed analysis with AI...")
    
    try:
        # Use hardcoded API key (temporary)
        api_key = OPENROUTER_API_KEY
        if not api_key:
            msg = "OpenAI API key not found. Please set OPENROUTER_API_KEY."
            print(f"[ERROR] {msg}")
            return f"Unable to generate detailed report: {msg}"

        client = OpenAI(base_url=OPENAI_BASE_URL, api_key=api_key)
        
        # Prepare the prompt
        stock_info = report.get("stock_information", {})
        news = report.get("news_summaries", [])
        
        stock_summary = "\n".join([f"- {k}: {v}" for k, v in stock_info.items()]) if stock_info else "No stock data available"
        news_summary = "\n".join([f"- Article {i+1}: {news[i][:200]}..." for i, _ in enumerate(news[:5])]) if news else "No news data available"
        
        prompt = f"""
You are a financial analyst. Create a comprehensive report about {company_name} based on the following data:

STOCK INFORMATION:
{stock_summary}

RECENT NEWS SUMMARIES:
{news_summary}

Please provide:
1. Company Overview - Brief description of the company
2. Stock Performance Analysis - Analysis of stock metrics and valuation
3. Market Position - Industry and sector analysis
4. Recent Events - Summary of recent news and developments
5. Key Insights & Recommendations - Your analysis and observations
6. Risk Factors - Potential risks to consider

Format the report professionally with clear sections and actionable insights.
"""
        
        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        detailed_content = getattr(response.choices[0].message, 'content', None)
        detailed_report = detailed_content if isinstance(detailed_content, str) and detailed_content.strip() else "[No detailed report returned]"
        print("[REPORT] Detailed report generated successfully.")
        return detailed_report
    
    except Exception as e:
        print(f"[ERROR] Error generating detailed report: {e}")
        return f"Unable to generate detailed report: {e}"

def get_stock_ticker(company_name: str) -> str:
    try:
        client = get_openai_client()
        if client is None:
            return "[Ticker unavailable: OPENROUTER_API_KEY not set]"

        prompt = (
            f"Return ONLY the official stock ticker symbol for the company '{company_name}'. "
            "Respond ONLY as JSON: {\"ticker\":\"TSLA\"}. "
            "Return {\"ticker\":\"NONE\"} if no ticker exists. "
            "Do not guess. Do not invent symbols."
        )

        response = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[
                {"role": "system", "content": "Strict JSON only. No text."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20
        )

        raw = getattr(response.choices[0].message, "content", "") or ""
        raw = raw.strip()

        import json
        ticker = json.loads(raw).get("ticker", "NONE")
        return ticker.upper()

    except Exception as e:
        return f"[Ticker lookup failed: {e}]"

def run_pipeline(query):
    
    company = extract_company_name(query)
    
    if not company:
        print("[ERROR] Could not extract company name from query.")
        return
    
    print(f"[SUCCESS] Detected company: {company}")
    
    # Step 2: Fetch news
    news_summaries = fetch_news(company)
    
    ticker = get_stock_ticker(company)
    print(f"[INFO] Detected ticker symbol: {ticker}")
    
    # Step 3: Fetch stock information
    stock_info = fetch_stock_info(ticker)
    
    # Step 4: Aggregate information
    aggregated_report = aggregate_information(company, news_summaries, stock_info)
    
    # Step 5: Generate detailed report
    detailed_report = generate_detailed_report(company, aggregated_report)
    
    # Step 6: Display results
    print("\n" + "=" * 80)
    print("DETAILED ANALYSIS REPORT")
    print("=" * 80)
    print(detailed_report)
    print("=" * 80)
    
    # Save report to file
    try:
        output_dir = Path("output")
        output_dir.mkdir(exist_ok=True)
        report_filename = output_dir / f"report_{company.replace(' ', '_')}_{aggregated_report['timestamp'][:10]}.txt"
        
        with open(report_filename, 'w') as f:
            f.write(str("=" * 80) + "\n")
            f.write(str(f"FINANCIAL INTELLIGENCE REPORT: {company}\n"))
            f.write(str("=" * 80) + "\n\n")
            
            f.write("STOCK INFORMATION:\n")
            f.write(("-" * 40) + "\n")
            if stock_info:
                for k, v in stock_info.items():
                    f.write(f"{k}: {str(v)}\n")
            else:
                f.write("No stock information available\n")
            
            f.write("\n\nRECENT NEWS SUMMARIES:\n")
            f.write(("-" * 40) + "\n")
            for idx, summary in enumerate(news_summaries, 1):
                f.write(f"\nArticle {idx}:\n{str(summary)}\n")
            
            f.write("\n\nDETAILED ANALYSIS:\n")
            f.write(("-" * 40) + "\n")
            f.write(str(detailed_report))
        
        print(f"\n[SAVED] Report saved to: {report_filename}")
    except Exception as e:
        print(f"[WARNING] Could not save report: {e}")

def main():
    """Main entry point."""
    try:
        query = input("Enter a company name or topic: ").strip()
        
        if not query:
            print("Invalid input.")
            return
        
        run_pipeline(query)
    
    except KeyboardInterrupt:
        print("\n\n[INTERRUPTED] Pipeline cancelled by user.")
    except Exception as e:
        print(f"\n[FATAL ERROR] Unexpected error: {e}")

if __name__ == "__main__":
    main()
