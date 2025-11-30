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
