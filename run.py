#!/usr/bin/env python3
"""
Financial Intelligence Pipeline - Main Entry Point

This is the recommended starting script for the Financial Intelligence Pipeline.
It provides a clean, user-friendly interface to access all pipeline features.
"""

import sys
import os
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def print_banner():
    """Display welcome banner."""
    print("\n" + "="*80)
    print("╔" + "─"*78 + "╗")
    print("║" + " "*78 + "║")
    print("║" + "FINANCIAL INTELLIGENCE PIPELINE".center(78) + "║")
    print("║" + "Powered by AI-driven Market Analysis".center(78) + "║")
    print("║" + " "*78 + "║")
    print("╚" + "─"*78 + "╝")
    print("="*80)

def print_menu():
    """Display main menu."""
    print("\n" + "─"*80)
    print("MAIN MENU")
    print("─"*80)
    print("1. Generate Financial Report     - Full analysis with news + stock + AI insights")
    print("2. Extract Company Name          - Test company name extraction")
    print("3. Fetch News                    - Get recent news summaries")
    print("4. Get Stock Information         - Retrieve stock metrics")
    print("5. Run Component Tests           - Test all components")
    print("6. View Documentation            - Read guides and architecture")
    print("0. Exit                          - Quit the application")
    print("─"*80)

def option_generate_report():
    """Option 1: Generate full financial report."""
    print("\n" + "─"*80)
    print("GENERATE FINANCIAL REPORT")
    print("─"*80)
    
    query = input("Enter company name or topic: ").strip()
    
    if not query:
        print("✗ Invalid input.")
        return
    
    print("\nInitializing pipeline...")
    
    try:
        from src.core.pipeline import run_pipeline
        run_pipeline(query)
    except KeyboardInterrupt:
        print("\n\n✗ Report generation cancelled by user.")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()

def option_extract_company():
    """Option 2: Test company extraction."""
    print("\n" + "─"*80)
    print("EXTRACT COMPANY NAME")
    print("─"*80)
    
    query = input("Enter company name or topic: ").strip()
    
    if not query:
        print("✗ Invalid input.")
        return
    
    try:
        from src.modules.extract_company_name import extract_company_name
        
        print(f"\nProcessing: '{query}'")
        company = extract_company_name(query)
        
        if company:
            print(f"✓ Extracted company: {company}")
        else:
            print("✗ Could not extract company name.")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def option_fetch_news():
    """Option 3: Fetch and display news."""
    print("\n" + "─"*80)
    print("FETCH NEWS")
    print("─"*80)
    
    company = input("Enter company name: ").strip()
    
    if not company:
        print("✗ Invalid input.")
        return
    
    try:
        from src.modules.news_fetcher import get_news_content
        
        print(f"\nFetching news for: {company}")
        articles = get_news_content(company)
        
        if articles:
            print(f"✓ Found {len(articles)} articles\n")
            for idx, article in enumerate(articles, 1):
                print(f"─── Article {idx} ───")
                preview = article[:300] + "..." if len(article) > 300 else article
                print(preview)
                print()
        else:
            print("✗ No articles found.")
    
    except Exception as e:
        print(f"✗ Error: {e}")

def option_get_stock_info():
    """Option 4: Get stock information."""
    print("\n" + "─"*80)
    print("GET STOCK INFORMATION")
    print("─"*80)
    
    ticker = input("Enter stock ticker (e.g., AAPL, MSFT): ").strip().upper()
    
    if not ticker:
        print("✗ Invalid input.")
        return
    
    try:
        from src.modules.stock_info_formatter import print_stock_info
        
        print(f"\nFetching stock info for: {ticker}")
        print_stock_info(ticker)
    
    except Exception as e:
        print(f"✗ Error: {e}")

def option_run_tests():
    """Option 5: Run component tests."""
    print("\n" + "─"*80)
    print("RUNNING COMPONENT TESTS")
    print("─"*80)
    print("Starting tests (this may take a moment)...\n")
    
    try:
        import subprocess
        import sys
        
        result = subprocess.run(
            [sys.executable, "tests/test_pipeline.py"],
            cwd=Path(__file__).parent
        )
        
        if result.returncode == 0:
            print("\n✓ Tests completed successfully.")
        else:
            print(f"\n✗ Tests failed with code: {result.returncode}")
    
    except Exception as e:
        print(f"✗ Error running tests: {e}")

def option_view_docs():
    """Option 6: View documentation."""
    print("\n" + "─"*80)
    print("DOCUMENTATION")
    print("─"*80)
    print("1. README.md              - Main project introduction")
    print("2. QUICK_REFERENCE.md     - Quick reference card")
    print("3. USAGE_GUIDE.md         - Complete usage guide")
    print("4. ARCHITECTURE.md        - Technical architecture")
    print("0. Back to main menu")
    print("─"*80)
    
    choice = input("Select documentation to view: ").strip()
    
    docs = {
        "1": "README.md",
        "2": "QUICK_REFERENCE.md",
        "3": "USAGE_GUIDE.md",
        "4": "ARCHITECTURE.md"
    }
    
    if choice in docs:
        doc_file = Path(__file__).parent / "docs" / docs[choice]
        if doc_file.exists():
            with open(doc_file, 'r') as f:
                content = f.read()
                print("\n" + "─"*80)
                print(content)
                print("─"*80)
        else:
            print(f"✗ File not found: {doc_file}")
    elif choice != "0":
        print("✗ Invalid selection.")

def main():
    """Main entry point."""
    print_banner()
    
    try:
        while True:
            print_menu()
            choice = input("Select an option: ").strip()
            
            if choice == "1":
                option_generate_report()
            elif choice == "2":
                option_extract_company()
            elif choice == "3":
                option_fetch_news()
            elif choice == "4":
                option_get_stock_info()
            elif choice == "5":
                option_run_tests()
            elif choice == "6":
                option_view_docs()
            elif choice == "0":
                print("\n✓ Thank you for using Financial Intelligence Pipeline!")
                print("="*80 + "\n")
                break
            else:
                print("✗ Invalid selection. Please try again.")
    
    except KeyboardInterrupt:
        print("\n\n✓ Application closed.")
        print("="*80 + "\n")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
