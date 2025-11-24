import yfinance as yf

def get_stock_info(ticker):
    """Fetch and return stock information as a dictionary."""
    try:
        t = yf.Ticker(ticker)
        info = t.info
        
        sections = {
            "Company Info": ["longName", "shortName", "symbol", "industry", "sector", "website"],
            "Location": ["address1", "city", "state", "zip", "country"],
            "Market Data": [
                "currentPrice", "previousClose", "open", "dayHigh", "dayLow",
                "regularMarketChangePercent", "marketCap"
            ],
            "Valuation Metrics": ["trailingPE", "forwardPE", "priceToBook", "beta"],
            "Financials": [
                "totalRevenue", "grossProfits", "ebitda", "freeCashflow",
                "operatingCashflow", "revenueGrowth", "earningsGrowth"
            ],
            "Dividends & Splits": [
                "dividendRate", "dividendYield", "lastSplitFactor", "lastSplitDate"
            ],
            "Analyst Targets": [
                "targetHighPrice", "targetLowPrice", "targetMeanPrice", "recommendationKey"
            ]
        }
        
        result = {}
        for section, keys in sections.items():
            result[section] = {}
            for key in keys:
                if key in info:
                    result[section][key] = info[key]
        
        return result
    except Exception as e:
        print(f"Error fetching stock info: {e}")
        return None

def print_stock_info(ticker):
    """Print stock information in a formatted way."""
    stock_data = get_stock_info(ticker)
    
    if not stock_data:
        print(f"Could not fetch data for ticker: {ticker}")
        return
    
    print(f"\n==================== {ticker} ====================\n")
    
    for section, data in stock_data.items():
        print(f"\n=== {section} ===")
        for key, value in data.items():
            print(f"{key:25} : {value}")
