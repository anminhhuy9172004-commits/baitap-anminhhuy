import sqlite3
import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from email.utils import parsedate_to_datetime
from pathlib import Path


DB = Path(__file__).resolve().parent.parent / "news.db"


RSS_FEEDS = {
    "VnExpress": (
        "https://vnexpress.net/rss/tin-moi-nhat.rss",
        "vietnam",
    ),
    "Tuổi Trẻ": (
        "https://tuoitre.vn/rss/tin-moi-nhat.rss",
        "vietnam",
    ),
    "Thanh Niên": (
        "https://thanhnien.vn/rss/home.rss",
        "vietnam",
    ),
    "BBC": (
        "https://feeds.bbci.co.uk/news/world/rss.xml",
        "world",
    ),
    "Al Jazeera": (
        "https://www.aljazeera.com/xml/rss/all.xml",
        "world",
    ),
    "Reuters": (
        "https://feeds.reuters.com/reuters/worldNews",
        "world",
    ),
}


def make_news_id(url):
    return hashlib.sha256(
        url.strip().encode("utf-8")
    ).hexdigest()


def init_db():

    conn = sqlite3.connect(DB)

    columns = [
        row[1]
        for row in conn.execute(
            "PRAGMA table_info(news)"
        ).fetchall()
    ]

    if not columns:

        conn.execute("""
            CREATE TABLE news (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                news_id TEXT,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT,
                category TEXT,
                published_at TEXT,
                image TEXT,
                summary TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                region TEXT
            )
        """)

    else:

        if "news_id" not in columns:
            conn.execute(
                "ALTER TABLE news ADD COLUMN news_id TEXT"
            )

        if "image" not in columns:
            conn.execute(
                "ALTER TABLE news ADD COLUMN image TEXT"
            )

        if "summary" not in columns:
            conn.execute(
                "ALTER TABLE news ADD COLUMN summary TEXT"
            )

        if "region" not in columns:
            conn.execute(
                "ALTER TABLE news ADD COLUMN region TEXT"
            )

    # Tao news_id cho record cu neu thieu
    rows = conn.execute("""
        SELECT id, url
        FROM news
        WHERE
            (news_id IS NULL OR TRIM(news_id) = '')
            AND url IS NOT NULL
            AND TRIM(url) != ''
    """).fetchall()

    for row_id, url in rows:

        news_id = make_news_id(url)

        conn.execute("""
            UPDATE news
            SET news_id = ?
            WHERE id = ?
        """, (
            news_id,
            row_id,
        ))

    conn.commit()

    # Unique index
    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_news_unique_url
        ON news(url)
        WHERE url IS NOT NULL
          AND TRIM(url) != ''
    """)

    conn.execute("""
        CREATE UNIQUE INDEX IF NOT EXISTS
        idx_news_unique_news_id
        ON news(news_id)
        WHERE news_id IS NOT NULL
          AND TRIM(news_id) != ''
    """)

    conn.commit()
    conn.close()


def clean_text(value):

    if not value:
        return ""

    value = html.unescape(value)

    value = re.sub(
        r"<[^>]+>",
        "",
        value
    )

    return " ".join(
        value.split()
    ).strip()


def fetch_feed(url):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent":
                "Mozilla/5.0 NewsCrawler/1.0"
        },
    )

    with urllib.request.urlopen(
        request,
        timeout=15
    ) as response:

        return response.read()


def parse_date(value):

    if not value:
        return None

    try:
        return parsedate_to_datetime(
            value
        ).isoformat()

    except Exception:
        return value


def parse_feed(
    xml_data,
    source,
    region
):

    root = ET.fromstring(xml_data)

    items = []

    for item in root.findall(".//item"):

        title = clean_text(
            item.findtext("title")
        )

        url = clean_text(
            item.findtext("link")
        )

        summary = clean_text(
            item.findtext("description")
        )

        pub_date = parse_date(
            clean_text(
                item.findtext("pubDate")
            )
        )

        if not title or not url:
            continue

        category = (
            "world"
            if region == "world"
            else "general"
        )

        items.append({
            "news_id": make_news_id(url),
            "title": title,
            "url": url,
            "summary": summary,
            "source": source,
            "category": category,
            "region": region,
            "published_at": pub_date,
        })

    return items


def save_news(items):

    conn = sqlite3.connect(DB)

    new_count = 0
    skipped_count = 0

    for item in items:

        news_id = item["news_id"]
        url = item["url"]

        exists = conn.execute("""
            SELECT id
            FROM news
            WHERE
                news_id = ?
                OR url = ?
            LIMIT 1
        """, (
            news_id,
            url,
        )).fetchone()

        if exists:

            skipped_count += 1
            continue

        try:

            cursor = conn.execute("""
                INSERT INTO news
                (
                    news_id,
                    title,
                    url,
                    source,
                    category,
                    published_at,
                    summary,
                    region
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                news_id,
                item["title"],
                url,
                item["source"],
                item["category"],
                item["published_at"],
                item["summary"],
                item["region"],
            ))

            if cursor.rowcount == 1:
                new_count += 1

        except sqlite3.IntegrityError:

            skipped_count += 1

        except Exception as error:

            print(
                "[NEWS] Save error:",
                error
            )

    conn.commit()
    conn.close()

    return new_count, skipped_count


def crawl_news():

    init_db()

    print("=" * 60)
    print("NEWS CRAWLER")
    print("=" * 60)

    all_items = []

    for source, config in RSS_FEEDS.items():

        feed_url, region = config

        try:

            xml_data = fetch_feed(
                feed_url
            )

            items = parse_feed(
                xml_data,
                source,
                region
            )

            all_items.extend(items)

            print(
                f"[NEWS] {source}: "
                f"{len(items)} articles "
                f"({region})"
            )

        except Exception as error:

            print(
                f"[NEWS] {source} ERROR:",
                error
            )

    # Chống trùng trong chính lần crawl này
    unique = {}

    for item in all_items:

        unique[item["url"]] = item

    all_items = list(
        unique.values()
    )

    new_count, skipped_count = save_news(
        all_items
    )

    print(
        f"[NEWS] Total: {len(all_items)} | "
        f"New: {new_count} | "
        f"Skipped: {skipped_count}"
    )

    return {
        "total": len(all_items),
        "new": new_count,
        "skipped": skipped_count,
    }


if __name__ == "__main__":

    result = crawl_news()

    print()
    print("RESULT:")
    print(result)
