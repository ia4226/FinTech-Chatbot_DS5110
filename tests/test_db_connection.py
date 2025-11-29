"""Database connectivity tests for the FinTech chatbot."""
from __future__ import annotations

import os
import uuid

import psycopg
import pytest
from dotenv import load_dotenv

# Ensure .env is loaded so DATABASE_URL is available when running pytest directly.
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

pytestmark = pytest.mark.skipif(
    not DATABASE_URL,
    reason="DATABASE_URL is not configured; set it in the environment or .env to run DB tests.",
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


def test_save_stock_snapshot_inserts_row():
    """Ensure save_stock_snapshot creates the table and inserts a row."""
    from src.core.db import save_stock_snapshot

    unique_ticker = f"TEST{uuid.uuid4().hex[:6].upper()}"
    stock_payload = {
        "ticker": unique_ticker,
        "longName": "Integration Test Corp",
        "sector": "Testing",
        "industry": "Integration QA",
        "currentPrice": 123.45,
        "marketCap": 1_000_000,
        "trailingPE": 21.5,
        "dividendYield": None,
        "52WeekHigh": 150.0,
        "52WeekLow": 90.0,
        "totalRevenue": 2_500_000,
        "freeCashflow": 800_000,
        "website": "https://example.com",
    }

    save_stock_snapshot(stock_payload)

    with _connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ticker FROM stock_snapshots WHERE ticker = %s ORDER BY captured_at DESC LIMIT 1",
                (unique_ticker,),
            )
            stored = cur.fetchone()
            # Clean up so the test can run repeatedly without unbounded growth.
            cur.execute("DELETE FROM stock_snapshots WHERE ticker = %s", (unique_ticker,))
            conn.commit()

    assert stored is not None and stored[0] == unique_ticker
