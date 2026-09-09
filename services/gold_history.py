import sqlite3
from datetime import datetime, timedelta


DB_FILE = "gold_history.db"


def get_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_gold_db():
    conn = get_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS gold_prices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            symbol TEXT NOT NULL,
            price REAL NOT NULL,
            currency TEXT NOT NULL,
            unit TEXT DEFAULT 'USD/oz',
            source TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_gold_prices_symbol_time
        ON gold_prices(symbol, updated_at)
    """)

    conn.commit()
    conn.close()


def save_gold_price(
    symbol: str,
    price: float,
    currency: str = "USD",
    unit: str = "USD/oz",
    source: str = "Gold API",
    updated_at: str | None = None
):

    if updated_at is None:
        updated_at = datetime.now().isoformat()

    conn = get_connection()

    conn.execute(
        """
        INSERT INTO gold_prices
        (
            symbol,
            price,
            currency,
            unit,
            source,
            updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            price,
            currency,
            unit,
            source,
            updated_at
        )
    )

    conn.commit()
    conn.close()


def get_gold_history(
    symbol: str = "XAU",
    hours: int = 24
):

    since = datetime.now() - timedelta(hours=hours)

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            symbol,
            price,
            currency,
            unit,
            source,
            updated_at
        FROM gold_prices
        WHERE symbol = ?
          AND updated_at >= ?
        ORDER BY updated_at ASC
        """,
        (
            symbol,
            since.isoformat()
        )
    ).fetchall()

    conn.close()

    return [
        {
            "symbol": row["symbol"],
            "price": row["price"],
            "currency": row["currency"],
            "unit": row["unit"],
            "source": row["source"],
            "updated_at": row["updated_at"]
        }
        for row in rows
    ]


def get_latest_gold_price(
    symbol: str = "XAU"
):

    conn = get_connection()

    row = conn.execute(
        """
        SELECT
            symbol,
            price,
            currency,
            unit,
            source,
            updated_at
        FROM gold_prices
        WHERE symbol = ?
        ORDER BY updated_at DESC
        LIMIT 1
        """,
        (symbol,)
    ).fetchone()

    conn.close()

    if row is None:
        return None

    return {
        "symbol": row["symbol"],
        "price": row["price"],
        "currency": row["currency"],
        "unit": row["unit"],
        "source": row["source"],
        "updated_at": row["updated_at"]
    }


def cleanup_gold_history(days: int = 30):

    cutoff = datetime.now() - timedelta(days=days)

    conn = get_connection()

    conn.execute(
        """
        DELETE FROM gold_prices
        WHERE updated_at < ?
        """,
        (cutoff.isoformat(),)
    )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    init_gold_db()

    print(
        "Gold history database initialized."
    )