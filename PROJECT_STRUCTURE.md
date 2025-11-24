# Financial Intelligence Pipeline - Reorganized Structure

## 📁 New Project Structure

```
Project/
├── run.py                          ⭐ Main entry point - Start here!
├── README.md                       📖 Project documentation
├── requirements.txt                📦 Python dependencies
│
├── src/                            🔧 Source code
│   ├── __init__.py
│   ├── core/                       Core pipeline logic
│   │   ├── __init__.py
│   │   └── pipeline.py            Main orchestrator
│   │
│   └── modules/                    Functional modules
│       ├── __init__.py
│       ├── extract_company_name.py Company extraction
│       ├── news_fetcher.py        News fetching
│       └── stock_info_formatter.py Stock data
│
├── tests/                          ✅ Testing
│   └── test_pipeline.py           Component tests
│
├── data/                           📊 Data files
│   └── companies.csv              S&P 500 list
│
├── docs/                           📚 Documentation
│   ├── README.md
│   ├── QUICK_REFERENCE.md
│   ├── USAGE_GUIDE.md
│   ├── ARCHITECTURE.md
│   ├── DIAGRAMS.md
│   ├── PROJECT_SUMMARY.md
│   ├── PIPELINE_README.md
│   ├── BUILD_SUMMARY.md
│   ├── INDEX.md
│   └── COMPLETION_CERTIFICATE.md
│
├── output/                         📄 Generated reports
│   └── report_*.txt               Financial reports
│
├── config/                         ⚙️  Configuration
│   └── (for future configs)
│
├── venv/                           Python environment
├── backend/                        (Legacy - keep for reference)
├── datasets/                       (Legacy - moved to data/)
└── frontend/                       (Empty - for future UI)
```

## 🚀 Quick Start

### Before First Run
1. Move `datasets/companies.csv` to `data/companies.csv` (if not already there)

### Run the Pipeline
```bash
# Interactive menu with all features
python run.py

# Or run directly
python -m src.core.pipeline

# Or run tests
python tests/test_pipeline.py
```

## 📂 Directory Explanations

### `/src` - Source Code
- **core/** - Core pipeline orchestration logic
  - `pipeline.py` - Main coordinator that ties everything together
  
- **modules/** - Individual functional modules
  - `extract_company_name.py` - Company name extraction logic
  - `news_fetcher.py` - News article fetching and parsing
  - `stock_info_formatter.py` - Stock data retrieval and formatting

### `/tests` - Testing
- Component validation tests
- Integration tests
- Run with: `python tests/test_pipeline.py`

### `/data` - Data Files
- `companies.csv` - S&P 500 company list used for extraction

### `/docs` - Documentation
- All markdown documentation files
- Organized guides, architecture docs, references

### `/output` - Generated Reports
- Timestamped financial intelligence reports
- Automatically created when pipeline runs

### `/config` - Configuration
- For future configuration files
- Environment-specific settings

## 🔗 Module Dependencies

```
run.py
  └─> src.core.pipeline
       ├─> src.modules.extract_company_name
       ├─> src.modules.news_fetcher
       ├─> src.modules.stock_info_formatter
       └─> External APIs (BBC, yfinance, OpenRouter)

tests/test_pipeline.py
  ├─> src.modules.extract_company_name
  ├─> src.modules.news_fetcher
  ├─> src.modules.stock_info_formatter
  └─> External APIs
```

## ✅ Key Improvements

### Before (Messy)
- Root folder had 15+ files mixed together
- Documentation scattered throughout
- No clear separation of concerns
- Unclear which files to run

### After (Organized)
- ✅ Clean root with only `run.py` and main files
- ✅ Source code in `/src` with logical grouping
- ✅ Tests in `/tests` folder
- ✅ Documentation in `/docs` folder
- ✅ Generated output in `/output` folder
- ✅ Data files in `/data` folder
- ✅ Clear module hierarchy
- ✅ Easy to navigate and maintain

## 📖 Documentation Navigation

| File | Location | Purpose |
|------|----------|---------|
| README.md | `/docs` | Project overview |
| QUICK_REFERENCE.md | `/docs` | Command reference |
| USAGE_GUIDE.md | `/docs` | Usage instructions |
| ARCHITECTURE.md | `/docs` | Technical design |
| DIAGRAMS.md | `/docs` | Visual diagrams |
| PROJECT_SUMMARY.md | `/docs` | Project details |
| PIPELINE_README.md | `/docs` | Complete docs |
| INDEX.md | `/docs` | Doc index |

## 🔧 Modules Overview

### extract_company_name.py
- **Purpose**: Extract company names from user queries
- **Key Functions**:
  - `extract_company_name(query)` - Main extraction function
  - `load_sp500()` - Load company database
  - `normalize_text()`, `clean_text()` - Text processing
- **Input**: User query string
- **Output**: Standardized company name

### news_fetcher.py
- **Purpose**: Fetch and parse news articles
- **Key Functions**:
  - `get_news_content(topic)` - Main function
  - `get_bbc_news_content()` - BBC search
  - `extract_hrefs()` - Extract article links
  - `extract_paragraphs()` - Extract content
- **Input**: Company name
- **Output**: List of article texts

### stock_info_formatter.py
- **Purpose**: Retrieve and format stock data
- **Key Functions**:
  - `get_stock_info(ticker)` - Fetch structured data
  - `print_stock_info()` - Display formatted output
- **Input**: Stock ticker
- **Output**: Dictionary of stock metrics

### pipeline.py
- **Purpose**: Orchestrate all components
- **Key Functions**:
  - `run_pipeline(query)` - Main orchestrator
  - `fetch_news()`, `fetch_stock_info()` - Data collection
  - `generate_detailed_report()` - AI analysis
  - `aggregate_information()` - Data combination
  - `load_summarizer()`, `safe_summarize()` - Summarization
- **Input**: User query
- **Output**: Complete financial report

## 🎯 Import Paths

### Old Way (Still Works)
```python
from backend.extract_company_name import extract_company_name
from backend.news_fetcher import get_news_content
from backend.stock_info_formatter import get_stock_info
```

### New Way (Recommended)
```python
from src.modules.extract_company_name import extract_company_name
from src.modules.news_fetcher import get_news_content
from src.modules.stock_info_formatter import get_stock_info
from src.core.pipeline import run_pipeline
```

## 🔄 Migration Notes

### Legacy Files
The following files remain for backward compatibility:
- `backend/` folder - Original module location
- `datasets/` folder - Original data location
- `main.py`, `start.py`, `test.py` - Original test files

### Recommended
Use the new structure:
- Run: `python run.py`
- Import from: `src.modules.*` and `src.core.*`
- Store data in: `data/` folder
- Store docs in: `docs/` folder

## 📦 Adding New Features

### Add a New Module
1. Create file in `src/modules/`
2. Follow existing module patterns
3. Import in `src/core/pipeline.py`
4. Test in `tests/`

### Add Configuration
1. Create config file in `config/`
2. Load in `run.py` or module
3. Document in `docs/`

### Add Documentation
1. Create markdown file in `docs/`
2. Link from main README
3. Update INDEX.md

## ✨ Benefits of New Structure

1. **Clarity** - Clear separation of concerns
2. **Scalability** - Easy to add new modules
3. **Maintainability** - Logical organization
4. **Professionalism** - Looks polished and organized
5. **Navigation** - Easy to find files
6. **Testing** - Centralized test location
7. **Documentation** - Organized in one place
8. **Distribution** - Ready for packaging
9. **Collaboration** - Clear structure for teams
10. **Standardization** - Follows Python best practices

## 🚀 Next Steps

1. Update any imports in your code
2. Run `python run.py` to test
3. Review `docs/README.md` for help
4. Follow the organized structure for new features

## 📞 Support

- **Quick Help**: See `docs/QUICK_REFERENCE.md`
- **Full Docs**: See `docs/README.md`
- **Architecture**: See `docs/ARCHITECTURE.md`
- **Tests**: Run `python tests/test_pipeline.py`

---

**Enjoy the cleaner, more professional project structure! 🎉**
