import json
from src.modules.extract_company_name import extract_company_name
from src.modules.news_fetcher import get_news_content
from src.modules.stock_info_formatter import get_stock_info
from transformers import pipeline
from openai import OpenAI
import yfinance as yf
import sys
from datetime import datetime
from pathlib import Path

# Initialize summarizer
def load_summarizer():
    """Load the summarization model."""
    try:
        print("Loading summarization model...")
        return pipeline("summarization", model="facebook/bart-large-cnn")
    except Exception as e:
        print(f"Error loading summarizer: {e}")
        return None

def safe_summarize(summarizer, text, max_chars=1500):
    """Safely summarize text with dynamic length adjustment."""
    try:
        if not text or len(text.strip()) < 50:
            return text
        
        tokens = text.split()
        token_len = len(tokens)

        if token_len < 80:
            max_len = 50
        elif token_len < 200:
            max_len = 100
        else:
            max_len = 250

        result = summarizer(text, max_length=max_len, min_length=30, do_sample=False)
        return result[0]["summary_text"] if result else text
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
        
        # Limit to 5 articles
        contents = contents[:5]
        print(f"[NEWS] Found {len(contents)} articles. Summarizing...")
        
        summarizer = load_summarizer()
        if not summarizer:
            print("[WARNING] Summarizer not available, returning raw content.")
            return contents[:3]  # Return first 3 raw articles
        
        summaries = []
        for idx, article_text in enumerate(contents, start=1):
            print(f"  - Summarizing article {idx}/{len(contents)}...")
            chunks = chunk_text(article_text)
            partial = []
            
            for c in chunks:
                summary = safe_summarize(summarizer, c)
                partial.append(summary)
            
            combined = " ".join(partial)
            if len(combined) > 100:
                final_summary = safe_summarize(summarizer, combined)
            else:
                final_summary = combined
            
            summaries.append(final_summary)
        
        return summaries
    except Exception as e:
        print(f"[ERROR] Error fetching news: {e}")
        return []

def fetch_stock_info(company_name):
    """Fetch stock information for the company."""
    print(f"\n[FETCHING STOCK INFO] Retrieving stock data for {company_name}...")
    try:
        # Try to get ticker from yfinance
        ticker_search = yf.Ticker(company_name)
        if not ticker_search.info or not ticker_search.info.get('symbol'):
            # Try company name as is
            ticker = company_name
        else:
            ticker = ticker_search.info.get('symbol', company_name)
        
        t = yf.Ticker(ticker)
        info = t.info
        
        if not info or info.get('symbol') is None:
            print(f"[WARNING] Could not fetch stock info for {company_name}")
            return None
        
        # Extract key information
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
        
        print("[STOCK] Stock data retrieved successfully.")
        return stock_data
    except Exception as e:
        print(f"[ERROR] Error fetching stock info: {e}")
        return None

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
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="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",
        )
        
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
        
        detailed_report = response.choices[0].message.content
        print("[REPORT] Detailed report generated successfully.")
        return detailed_report
    
    except Exception as e:
        print(f"[ERROR] Error generating detailed report: {e}")
        return f"Unable to generate detailed report: {e}"

def run_pipeline(query):
    """Main pipeline function that orchestrates all components."""
    print("=" * 80)
    print("FINANCIAL INTELLIGENCE PIPELINE")
    print("=" * 80)
    
    # Step 1: Extract company name
    print(f"\n[STEP 1] Extracting company name from query: '{query}'")
    company = extract_company_name(query)
    
    if not company:
        print("[ERROR] Could not extract company name from query.")
        return
    
    print(f"[SUCCESS] Detected company: {company}")
    
    # Step 2: Fetch news
    news_summaries = fetch_news(company)
    
    # Step 3: Fetch stock information
    stock_info = fetch_stock_info(company)
    
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
            f.write("=" * 80 + "\n")
            f.write(f"FINANCIAL INTELLIGENCE REPORT: {company}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("STOCK INFORMATION:\n")
            f.write("-" * 40 + "\n")
            if stock_info:
                for k, v in stock_info.items():
                    f.write(f"{k}: {v}\n")
            else:
                f.write("No stock information available\n")
            
            f.write("\n\nRECENT NEWS SUMMARIES:\n")
            f.write("-" * 40 + "\n")
            for idx, summary in enumerate(news_summaries, 1):
                f.write(f"\nArticle {idx}:\n{summary}\n")
            
            f.write("\n\nDETAILED ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            f.write(detailed_report)
        
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
