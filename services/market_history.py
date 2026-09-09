import sqlite3
from datetime import datetime
from pathlib import Path


DB = Path(__file__).resolve().parent.parent / "market_history.db"


def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS market_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT,
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Xóa duplicate trước khi tạo UNIQUE INDEX
    conn.execute("""
        DELETE FROM market_history
        WHERE id NOT IN (
            SELECT MIN(id)
            FROM market_history
            GROUP BY symbol, source, updated_at
        )
    """)

    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_market_history_unique
        ON market_history(symbol, source, updated_at)
    """)

    conn.commit()
    conn.close()


def save_price(
    symbol,
    price,
    currency,
    source,
    updated_at=None
):
    if price is None:
        return

    if updated_at is None:
        updated_at = datetime.now().isoformat()

    conn = sqlite3.connect(DB)

    conn.execute(
        """
        INSERT OR IGNORE INTO market_history
        (
            symbol,
            price,
            currency,
            source,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            symbol,
            float(price),
            currency,
            source,
            updated_at
        )
    )

    conn.commit()
    conn.close()


def get_history(
    symbol,
    hours=24
):
    conn = sqlite3.connect(DB)

    if symbol in ("Brent", "WTI"):
        rows = conn.execute(
            """
            SELECT
                symbol,
                price,
                currency,
                source,
                updated_at
            FROM market_history
            WHERE symbol = ?
              AND source = 'Yahoo Finance'
              AND updated_at >= datetime('now', ?)
            ORDER BY updated_at ASC
            """,
            (
                symbol,
                f"-{hours} hours"
            )
        ).fetchall()

    else:
        rows = conn.execute(
            """
            SELECT
                symbol,
                price,
                currency,
                source,
                updated_at
            FROM market_history
            WHERE symbol = ?
              AND updated_at >= datetime('now', ?)
            ORDER BY updated_at ASC
            """,
            (
                symbol,
                f"-{hours} hours"
            )
        ).fetchall()

    conn.close()

    return [
        {
            "symbol": row[0],
            "price": row[1],
            "currency": row[2],
            "source": row[3],
            "updated_at": row[4]
        }
        for row in rows
    ]