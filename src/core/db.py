"""Database helpers for persisting stock information snapshots."""
from __future__ import annotations

import json
import os
from typing import Any, Mapping

from dotenv import load_dotenv
import psycopg

# Ensure .env values are loaded even when this module is imported before pipeline.py
load_dotenv()

def _get_database_url() -> str | None:
    return os.getenv("DATABASE_URL")

_TABLE_READY = False

LATEST_SNAPSHOT_CTE = """
WITH latest AS (
    SELECT DISTINCT ON (ticker)
        ticker,
        long_name,
        sector,
        industry,
        current_price,
        market_cap,
        trailing_pe,
        dividend_yield,
        week_52_high,
        week_52_low,
        total_revenue,
        free_cashflow,
        website,
        captured_at
    FROM stock_snapshots
    ORDER BY ticker, captured_at DESC
)
"""

ANALYSIS_QUERIES = {
    "top_market_cap": {
        "title": "Top Market Cap Leaders",
        "description": "Companies with the highest recorded market capitalization.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, sector, market_cap, captured_at
        FROM latest
        ORDER BY market_cap DESC NULLS LAST
        LIMIT 10;
        """,
    },
    "value_pe": {
        "title": "Lowest Trailing P/E",
        "description": "Potentially undervalued companies based on trailing P/E ratio.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, trailing_pe, sector, captured_at
        FROM latest
        WHERE trailing_pe IS NOT NULL AND trailing_pe > 0
        ORDER BY trailing_pe ASC
        LIMIT 10;
        """,
    },
    "dividend_yield": {
        "title": "Dividend Yield Standouts",
        "description": "Highest dividend yields across the latest snapshots.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, dividend_yield, sector, captured_at
        FROM latest
        WHERE dividend_yield IS NOT NULL AND dividend_yield > 0
        ORDER BY dividend_yield DESC
        LIMIT 10;
        """,
    },
    "revenue_leaders": {
        "title": "Largest Total Revenue",
        "description": "Top companies by total revenue reported in the snapshot.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, total_revenue, sector, captured_at
        FROM latest
        WHERE total_revenue IS NOT NULL
        ORDER BY total_revenue DESC
        LIMIT 10;
        """,
    },
    "cash_flow_kings": {
        "title": "Strongest Free Cashflow",
        "description": "Companies producing the most free cashflow.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, free_cashflow, sector, captured_at
        FROM latest
        WHERE free_cashflow IS NOT NULL
        ORDER BY free_cashflow DESC
        LIMIT 10;
        """,
    },
    "high_price_to_high": {
        "title": "Closest to 52-Week High",
        "description": "Stocks trading nearest to their 52-week high.",
        "sql": LATEST_SNAPSHOT_CTE + """
         SELECT ticker,
             long_name,
             current_price,
             week_52_high,
             ROUND(((current_price / NULLIF(week_52_high, 0)) * 100)::numeric, 2) AS pct_of_high,
               captured_at
        FROM latest
        WHERE current_price IS NOT NULL AND week_52_high IS NOT NULL AND week_52_high > 0
        ORDER BY pct_of_high DESC
        LIMIT 5;
        """,
    },
    "high_volatility": {
        "title": "Largest 52-Week Range",
        "description": "Stocks with the widest gap between 52-week high and low.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker,
               long_name,
               week_52_high,
               week_52_low,
               (week_52_high - week_52_low) AS range,
               captured_at
        FROM latest
        WHERE week_52_high IS NOT NULL AND week_52_low IS NOT NULL
        ORDER BY range DESC
        LIMIT 10;
        """,
    },
    "sector_market_cap": {
        "title": "Average Market Cap by Sector",
        "description": "Aggregated average market cap per sector.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT sector,
               COUNT(*) AS companies,
               ROUND(AVG(market_cap)::NUMERIC, 2) AS avg_market_cap
        FROM latest
        WHERE sector IS NOT NULL AND market_cap IS NOT NULL
        GROUP BY sector
        ORDER BY avg_market_cap DESC
        LIMIT 15;
        """,
    },
    "sector_presence": {
        "title": "Company Count by Sector",
        "description": "How many tracked companies operate in each sector.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT sector,
               COUNT(*) AS companies
        FROM latest
        WHERE sector IS NOT NULL
        GROUP BY sector
        ORDER BY companies DESC
        LIMIT 15;
        """,
    },
    "recent_snapshots": {
        "title": "Most Recent Snapshots",
        "description": "The latest 5 records ingested into the database.",
        "sql": """
        SELECT ticker, long_name, sector, captured_at, current_price
        FROM stock_snapshots
        ORDER BY captured_at DESC
        LIMIT 5;
        """,
    },
    "price_leaders": {
        "title": "Highest Share Prices",
        "description": "Companies with the highest current trading price.",
        "sql": LATEST_SNAPSHOT_CTE + """
        SELECT ticker, long_name, current_price, sector, captured_at
        FROM latest
        WHERE current_price IS NOT NULL
        ORDER BY current_price DESC
        LIMIT 10;
        """,
    },
    "discount_vs_high": {
        "title": "Greatest Discount vs 52-Week High",
        "description": "Stocks trading furthest below their 52-week highs.",
        "sql": LATEST_SNAPSHOT_CTE + """
         SELECT ticker,
             long_name,
             current_price,
             week_52_high,
             ROUND((((week_52_high - current_price) / NULLIF(week_52_high, 0)) * 100)::numeric, 2) AS discount_pct,
               captured_at
        FROM latest
        WHERE current_price IS NOT NULL AND week_52_high IS NOT NULL AND week_52_high > 0
        ORDER BY discount_pct DESC
        LIMIT 5;
        """,
    },
}

CREATE_STOCK_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS stock_snapshots (
    id SERIAL PRIMARY KEY,
    ticker TEXT NOT NULL,
    long_name TEXT,
    sector TEXT,
    industry TEXT,
    current_price DOUBLE PRECISION,
    market_cap DOUBLE PRECISION,
    trailing_pe DOUBLE PRECISION,
    dividend_yield DOUBLE PRECISION,
    week_52_high DOUBLE PRECISION,
    week_52_low DOUBLE PRECISION,
    total_revenue DOUBLE PRECISION,
    free_cashflow DOUBLE PRECISION,
    website TEXT,
    raw_payload JSONB NOT NULL,
    captured_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
"""

INSERT_STOCK_SQL = """
INSERT INTO stock_snapshots (
    ticker,
    long_name,
    sector,
    industry,
    current_price,
    market_cap,
    trailing_pe,
    dividend_yield,
    week_52_high,
    week_52_low,
    total_revenue,
    free_cashflow,
    website,
    raw_payload
) VALUES (
    %(ticker)s,
    %(long_name)s,
    %(sector)s,
    %(industry)s,
    %(current_price)s,
    %(market_cap)s,
    %(trailing_pe)s,
    %(dividend_yield)s,
    %(week_52_high)s,
    %(week_52_low)s,
    %(total_revenue)s,
    %(free_cashflow)s,
    %(website)s,
    %(raw_payload)s
);
"""


def _coerce_numeric(value: Any) -> float | None:
    """Return a float for numeric values, otherwise None."""
    if value in (None, "N/A"):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _prepare_payload(stock_data: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "ticker": stock_data.get("ticker"),
        "long_name": stock_data.get("longName"),
        "sector": stock_data.get("sector"),
        "industry": stock_data.get("industry"),
        "current_price": _coerce_numeric(stock_data.get("currentPrice")),
        "market_cap": _coerce_numeric(stock_data.get("marketCap")),
        "trailing_pe": _coerce_numeric(stock_data.get("trailingPE")),
        "dividend_yield": _coerce_numeric(stock_data.get("dividendYield")),
        "week_52_high": _coerce_numeric(stock_data.get("52WeekHigh")),
        "week_52_low": _coerce_numeric(stock_data.get("52WeekLow")),
        "total_revenue": _coerce_numeric(stock_data.get("totalRevenue")),
        "free_cashflow": _coerce_numeric(stock_data.get("freeCashflow")),
        "website": stock_data.get("website"),
        "raw_payload": json.dumps(stock_data, default=str),
    }


def _ensure_table(conn: psycopg.Connection) -> None:
    global _TABLE_READY
    if _TABLE_READY:
        return
    with conn.cursor() as cur:
        cur.execute(CREATE_STOCK_TABLE_SQL)
    _TABLE_READY = True


def save_stock_snapshot(stock_data: Mapping[str, Any]) -> None:
    """Persist the stock data into PostgreSQL.

    When DATABASE_URL is not configured the function logs and returns.
    """
    database_url = _get_database_url()
    if not database_url:
        print("[DB] DATABASE_URL not set; skipping persistence.")
        return

    payload = _prepare_payload(stock_data)
    if not payload.get("ticker"):
        print("[DB] Missing ticker symbol; skipping persistence.")
        return

    try:
        with psycopg.connect(database_url) as conn:
            _ensure_table(conn)
            with conn.cursor() as cur:
                cur.execute(INSERT_STOCK_SQL, payload)
            conn.commit()
        print("[DB] Stock snapshot stored successfully.")
    except Exception as exc:
        print(f"[DB] Failed to store stock snapshot: {exc}")


def list_analysis_queries() -> list[dict[str, str]]:
    """Return metadata for the available predefined SQL insights."""
    return [
        {
            "id": key,
            "title": meta["title"],
            "description": meta["description"],
        }
        for key, meta in ANALYSIS_QUERIES.items()
    ]


def run_analysis_query(query_id: str) -> dict[str, Any]:
    """Execute the requested analysis query and return rows/columns."""
    if query_id not in ANALYSIS_QUERIES:
        raise ValueError(f"Unknown analysis id '{query_id}'")

    database_url = _get_database_url()
    if not database_url:
        raise ValueError("DATABASE_URL not configured; cannot run analysis")

    query_meta = ANALYSIS_QUERIES[query_id]
    rows: list[dict[str, Any]] = []

    try:
        with psycopg.connect(database_url) as conn:
            _ensure_table(conn)
            with conn.cursor() as cur:
                cur.execute(query_meta["sql"])  # type: ignore[arg-type]
                fetched = cur.fetchall()
                col_names = [desc[0] for desc in cur.description] if cur.description else []
                rows = [dict(zip(col_names, record)) for record in fetched]
    except Exception as exc:
        raise RuntimeError(f"Failed to run analysis '{query_id}': {exc}") from exc

    columns = list(rows[0].keys()) if rows else []
    return {
        "id": query_id,
        "title": query_meta["title"],
        "description": query_meta["description"],
        "columns": columns,
        "rows": rows,
    }
