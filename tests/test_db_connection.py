"""Database connectivity tests for the FinTech chatbot."""
from __future__ import annotations

import os

import psycopg
import pytest
from dotenv import load_dotenv

# Ensure .env is loaded so configuration values exist when running pytest directly.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL or not OPENROUTER_API_KEY,
    reason=(
        "DATABASE_URL or OPENROUTER_API_KEY missing; configure both in .env to run integration DB tests."
    ),
)

def _connect():
    """Return a psycopg connection using DATABASE_URL."""
    assert DATABASE_URL is not None, "DATABASE_URL must be set to connect to the database"
    return psycopg.connect(DATABASE_URL)


def test_database_connection_responds_to_select_one():
    """Basic sanity check that the configured PostgreSQL instance is reachable."""
    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            row = cur.fetchone()
    assert row is not None and row[0] == 1


def test_extract_real_stock_info_and_persist(monkeypatch):
    """Resolve a real ticker, fetch stock info, and confirm it is stored in PostgreSQL."""
    from src.core import pipeline

    company = os.getenv("TEST_COMPANY", "JP Morgan Chase")

    resolved_ticker = pipeline.get_stock_ticker(company)
    assert resolved_ticker and not resolved_ticker.startswith("["), "Ticker lookup failed"

    # Avoid a second LLM call within fetch_stock_info by monkeypatching.
    monkeypatch.setattr(pipeline, "get_stock_ticker", lambda _: resolved_ticker)

    stock_payload = pipeline.fetch_stock_info(company)
    assert stock_payload is not None, "fetch_stock_info returned no data"

    ticker = stock_payload.get("ticker")
    assert ticker and ticker != "N/A", "Stock payload missing ticker"

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ticker FROM stock_snapshots WHERE ticker = %s ORDER BY captured_at DESC LIMIT 1",
                (ticker,),
            )
            stored = cur.fetchone()
            # Clean up for deterministic reruns.
            #cur.execute("DELETE FROM stock_snapshots WHERE ticker = %s", (ticker,))
            conn.commit()

    assert stored is not None and stored[0] == ticker
