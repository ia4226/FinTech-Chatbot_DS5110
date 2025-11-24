from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn
import traceback

import sys
from pathlib import Path

# Ensure project root is on sys.path so `src` package can be imported when
# running this script directly (e.g. `python frontend\app.py`). When Python
# executes a script, sys.path[0] is the script's directory (frontend/), so
# we add the repository root (parent of frontend/) to allow `import src`.
PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import pipeline functions after updating sys.path
from src.core import pipeline
from src.modules.extract_company_name import extract_company_name

app = FastAPI(title="FinTech Chatbot Frontend")

# Serve static files using absolute path (project-root aware)
STATIC_DIR = PROJECT_ROOT / "frontend" / "static"
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

class QueryPayload(BaseModel):
    query: str

class CompanyPayload(BaseModel):
    company: str


def _index_to_date_str(idx) -> str:
    """Safely convert an index value to a date string.

    Many DataFrame indices are pandas Timestamps which expose `.date()`.
    Static type checkers (Pylance) may treat the index as `Hashable` and
    complain about `.date()`. Use a try/except fallback to `str(idx)`.
    """
    try:
        return str(idx.date())
    except Exception:
        return str(idx)

@app.get("/", response_class=HTMLResponse)
async def index():
    return FileResponse("frontend/static/index.html")

@app.post("/api/extract")
async def api_extract(payload: QueryPayload):
    try:
        company = extract_company_name(payload.query)
        return {"company": company}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/news")
async def api_news(payload: CompanyPayload):
    try:
        # Use pipeline's fetch_news which includes summarization
        summaries = pipeline.fetch_news(payload.company)
        return {"news_summaries": summaries}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock")
async def api_stock(payload: CompanyPayload):
    try:
        stock = pipeline.fetch_stock_info(payload.company)
        return {"stock_info": stock}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/stock/history")
async def api_stock_history(payload: CompanyPayload):
    try:
        import yfinance as yf
        ticker = payload.company
        t = yf.Ticker(ticker)
        # if company is a name, try to resolve
        hist = None
        try:
            hist = t.history(period='1y')
        except Exception:
            # try symbol from info
            info = t.info
            sym = info.get("symbol") if info else None
            if sym:
                t2 = yf.Ticker(sym)
                hist = t2.history(period='1y')

        if hist is None or hist.empty:
            return {"history": []}

        # Return dates and close prices
        data = [{"date": _index_to_date_str(idx), "close": float(row.Close)} for idx, row in hist.iterrows()]
        return {"history": data}
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/report")
async def api_report(payload: QueryPayload):
    try:
        # Orchestrate: extract, news, stock, aggregate, generate
        company = extract_company_name(payload.query)
        if not company:
            raise HTTPException(status_code=400, detail="Could not extract company name from query")

        news = pipeline.fetch_news(company)
        stock = pipeline.fetch_stock_info(company)
        
        # Get price history for chart
        import yfinance as yf
        ticker = stock.get('ticker', company) if isinstance(stock, dict) else company
        chart_data = []
        try:
            hist = yf.Ticker(ticker).history(period='1y')
            if hist is not None and not hist.empty:
                chart_data = [{"date": _index_to_date_str(idx), "close": float(row.Close)} for idx, row in hist.iterrows()]
        except:
            pass
        
        aggregated = pipeline.aggregate_information(company, news, stock)
        detailed = pipeline.generate_detailed_report(company, aggregated)

        return {
            "company": company,
            "stock_info": stock,
            "news_summaries": news,
            "detailed_report": detailed,
            "chart_data": chart_data
        }
    except HTTPException:
        raise
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
