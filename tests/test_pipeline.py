#!/usr/bin/env python3
"""
Test script for the Financial Intelligence Pipeline
Validates each component independently before running full pipeline
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from src.modules.extract_company_name import extract_company_name
from src.modules.news_fetcher import get_news_content
from src.modules.stock_info_formatter import get_stock_info
import yfinance as yf

def test_company_extraction():
    """Test company name extraction."""
    print("\n" + "="*80)
    print("TEST 1: Company Name Extraction")
    print("="*80)
    
    test_queries = [
        "Tell me about Apple",
        "Show me info on Microsoft",
        "What about Amazon",
        "Stock info for Tesla"
    ]
    
    for query in test_queries:
        company = extract_company_name(query)
        print(f"Query: '{query}'")
        print(f"Extracted: {company if company else 'FAILED'}\n")
    
    return True

def test_stock_info():
    """Test stock information fetching."""
    print("\n" + "="*80)
    print("TEST 2: Stock Information Fetching")
    print("="*80)
    
    test_tickers = ["AAPL", "MSFT", "GOOGL"]
    
    for ticker in test_tickers:
        try:
            print(f"\nFetching info for {ticker}...")
            t = yf.Ticker(ticker)
            info = t.info
            
            if info and info.get('symbol'):
                print(f"  ✓ Symbol: {info.get('symbol')}")
                print(f"  ✓ Name: {info.get('longName', 'N/A')}")
                print(f"  ✓ Price: ${info.get('currentPrice', 'N/A')}")
                print(f"  ✓ Market Cap: {info.get('marketCap', 'N/A')}")
            else:
                print(f"  ✗ Could not fetch data")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return True

def test_news_fetching():
    """Test news fetching (limited)."""
    print("\n" + "="*80)
    print("TEST 3: News Fetching (Preview)")
    print("="*80)
    
    companies = ["Apple", "Tesla"]
    
    for company in companies:
        print(f"\nFetching news for {company}...")
        try:
            contents = get_news_content(company)
            if contents:
                print(f"  ✓ Found {len(contents)} articles")
                for idx, content in enumerate(contents[:2], 1):
                    preview = content[:150] + "..." if len(content) > 150 else content
                    print(f"    Article {idx}: {preview}")
            else:
                print(f"  ✗ No articles found (this may be normal)")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    return True

def test_pipeline_components():
    """Test all components together."""
    print("\n" + "="*80)
    print("TEST 4: Full Pipeline Components Test")
    print("="*80)
    
    query = "Apple Inc"
    
    print(f"\nTesting with query: '{query}'")
    
    # Step 1: Extract company
    print("\n[1/3] Extracting company name...")
    company = extract_company_name(query)
    if company:
        print(f"  ✓ Success: {company}")
    else:
        print("  ✗ Failed: Could not extract company")
        return False
    
    # Step 2: Get stock info
    print("\n[2/3] Fetching stock information...")
    try:
        stock_info = get_stock_info("AAPL")
        if stock_info:
            print(f"  ✓ Success: Retrieved {len(stock_info)} sections of data")
        else:
            print("  ✗ Failed: Could not fetch stock info")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    # Step 3: Get news
    print("\n[3/3] Fetching news articles...")
    try:
        news = get_news_content(company)
        if news:
            print(f"  ✓ Success: Retrieved {len(news)} articles")
        else:
            print("  ✗ No articles found (network or BBC issue)")
    except Exception as e:
        print(f"  ✗ Error: {e}")
    
    return True

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("FINANCIAL INTELLIGENCE PIPELINE - COMPONENT TEST")
    print("="*80)
    
    try:
        # Run tests
        test_company_extraction()
        test_stock_info()
        test_pipeline_components()
        
        print("\n" + "="*80)
        print("ALL TESTS COMPLETED")
        print("="*80)
        print("\nTo run the full pipeline with report generation:")
        print("  python run.py")
        print("\n" + "="*80)
        
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user.")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
