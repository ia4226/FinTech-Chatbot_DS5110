from dotenv import load_dotenv
from openai import OpenAI
import yfinance as yf
import os
import re

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

def normalize_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r"[^a-zA-Z0-9 .&-]", "", text)
    text = re.sub(r"\s+", " ", text)
    return text

def get_openai_client():
    api_key = OPENROUTER_API_KEY
    if not api_key:
        return None
    return OpenAI(base_url=OPENAI_BASE_URL, api_key=api_key)

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

def extract_company_name(query):
    api_key = (
        os.environ.get("OPENAI_API_KEY")
        or os.environ.get("OPENROUTER_API_KEY")
    )
    base_url = os.environ.get("OPENAI_BASE_URL", "https://openrouter.ai/api/v1")

    if not api_key or OpenAI is None:
        return None

    client = OpenAI(base_url=base_url, api_key=api_key)

    prompt = (
        "Extract the company name from the query.\n"
        "Output ONLY the name.\n"
        "No punctuation. No quotes. No extra text.\n"
        "If no company exists, return NONE.\n"
        f"Query: {query}"
    )

    try:
        resp = client.chat.completions.create(
            model="x-ai/grok-4.1-fast",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20
        )
        content = getattr(resp.choices[0].message, "content", "")
        if not content:
            return None
        raw = content.strip()
    except:
        return None

    if raw.upper() == "NONE":
        return None

    name = normalize_text(raw)
    return name if name else None

def main():
    query = "Tell me information about Adobe"
    cmpny = extract_company_name(query)
    print("Company Name:", cmpny)

    if not cmpny:
        print("[ERROR] No company detected. Cannot fetch ticker.")
        return

    ticker = get_stock_ticker(cmpny)
    print("Ticker:", ticker)

    print(fetch_stock_info(ticker))

if __name__ == "__main__":
    main()
