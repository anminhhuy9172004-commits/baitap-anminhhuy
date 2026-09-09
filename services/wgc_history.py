import sqlite3
from pathlib import Path


DB_PATH = Path("wgc_reference.db")


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        DB_PATH
    )


# ============================================================
# INIT DATABASE
# ============================================================

def init_wgc_db():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gold_reference (
            id INTEGER PRIMARY KEY AUTOINCREMENT,

            symbol TEXT NOT NULL,

            price REAL NOT NULL,

            currency TEXT NOT NULL,

            unit TEXT NOT NULL,

            source TEXT NOT NULL,

            reference_date TEXT NOT NULL,

            updated_at TEXT NOT NULL,

            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()

    conn.close()

    print(
        "WGC reference database initialized."
    )


# ============================================================
# SAVE / UPDATE WGC REFERENCE
# ============================================================

def save_wgc_reference(
    symbol,
    price,
    currency,
    unit,
    source,
    reference_date,
    updated_at
):

    conn = get_connection()

    cursor = conn.cursor()


    # --------------------------------------------------------
    # Tìm dữ liệu cùng symbol + reference_date
    # --------------------------------------------------------

    cursor.execute(
        """
        SELECT
            id,
            price
        FROM gold_reference
        WHERE symbol = ?
        AND reference_date = ?
        LIMIT 1
        """,
        (
            symbol,
            reference_date
        )
    )


    existing = cursor.fetchone()


    # --------------------------------------------------------
    # Đã tồn tại
    # --------------------------------------------------------

    if existing:

        existing_id = existing[0]

        existing_price = existing[1]


        # ----------------------------------------------------
        # Giá không thay đổi
        # ----------------------------------------------------

        if float(existing_price) == float(price):

            conn.close()

            print(
                "WGC reference already exists:",
                reference_date,
                price
            )

            return False


        # ----------------------------------------------------
        # Cùng ngày nhưng giá đã thay đổi
        # -> UPDATE
        # ----------------------------------------------------

        cursor.execute(
            """
            UPDATE gold_reference

            SET
                price = ?,
                currency = ?,
                unit = ?,
                source = ?,
                updated_at = ?

            WHERE id = ?
            """,
            (
                price,
                currency,
                unit,
                source,
                updated_at,
                existing_id
            )
        )


        conn.commit()

        conn.close()


        print(
            "WGC REFERENCE UPDATED:",
            price,
            reference_date
        )


        return True


    # --------------------------------------------------------
    # Chưa tồn tại
    # -> INSERT
    # --------------------------------------------------------

    cursor.execute(
        """
        INSERT INTO gold_reference (
            symbol,
            price,
            currency,
            unit,
            source,
            reference_date,
            updated_at
        )

        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            symbol,
            price,
            currency,
            unit,
            source,
            reference_date,
            updated_at
        )
    )


    conn.commit()

    conn.close()


    print(
        "WGC REFERENCE SAVED:",
        price,
        reference_date
    )


    return True


# ============================================================
# GET LATEST REFERENCE
# ============================================================

def get_latest_wgc_reference(
    symbol="XAU"
):

    conn = get_connection()

    cursor = conn.cursor()


    cursor.execute(
        """
        SELECT
            symbol,
            price,
            currency,
            unit,
            source,
            reference_date,
            updated_at

        FROM gold_reference

        WHERE symbol = ?

        ORDER BY
            reference_date DESC,
            id DESC

        LIMIT 1
        """,
        (
            symbol,
        )
    )


    row = cursor.fetchone()

    conn.close()


    if not row:

        return None


    return {

        "symbol":
            row[0],

        "price":
            row[1],

        "currency":
            row[2],

        "unit":
            row[3],

        "source":
            row[4],

        "reference_date":
            row[5],

        "updated_at":
            row[6]

    }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    init_wgc_db()


    latest = get_latest_wgc_reference()


    print(
        "LATEST:",
        latest
    )