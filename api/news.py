import sqlite3
from pathlib import Path

from fastapi import APIRouter, Query


router = APIRouter(
    prefix="/news",
    tags=["News"]
)

DB = (
    Path(__file__).resolve()
    .parent.parent / "news.db"
)


def get_news(
    limit=30,
    category=None
):
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row

    if category:
        rows = con.execute("""
            SELECT *
            FROM news
            WHERE category = ?
            ORDER BY published_at DESC, id DESC
            LIMIT ?
        """, (
            category,
            limit
        )).fetchall()

    else:
        rows = con.execute("""
            SELECT *
            FROM news
            ORDER BY published_at DESC, id DESC
            LIMIT ?
        """, (
            limit,
        )).fetchall()

    con.close()

    return [
        dict(row)
        for row in rows
    ]


@router.get("")
def news(
    limit: int = Query(
        30,
        ge=1,
        le=500
    ),
    category: str | None = None
):
    data = get_news(
        limit,
        category
    )

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@router.get("/latest")
def latest():
    data = get_news(20)

    return {
        "status": "success",
        "count": len(data),
        "data": data
    }


@router.get("/categories")
def categories():
    con = sqlite3.connect(DB)

    rows = con.execute("""
        SELECT
            category,
            COUNT(*) AS count
        FROM news
        GROUP BY category
        ORDER BY count DESC
    """).fetchall()

    con.close()

    return {
        "status": "success",
        "data": [
            {
                "category": row[0],
                "count": row[1]
            }
            for row in rows
        ]
    }

