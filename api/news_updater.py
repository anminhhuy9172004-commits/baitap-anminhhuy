import sqlite3
import hashlib
import html
import re
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from email.utils import parsedate_to_datetime
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "news.db"

RSS_FEEDS = {
    "VnExpress": "https://vnexpress.net/rss/tin-moi-nhat.rss",
    "Tuổi Trẻ": "https://tuoitre.vn/rss/tin-moi-nhat.rss",
    "Thanh Niên": "https://thanhnien.vn/rss/home.rss",
}

CATEGORIES = {
    "chính trị": "politics",
    "thời sự": "society",
    "xã hội": "society",
    "pháp luật": "law",
    "giáo dục": "education",
    "y tế": "health",
    "sức khỏe": "health",
    "công nghệ": "technology",
    "kinh doanh": "business",
    "thể thao": "sports",
    "văn hóa": "culture",
    "giải trí": "entertainment",
    "thế giới": "world",
    "đời sống": "lifestyle",
    "giao thông": "traffic",
}


def init_db():
    con = sqlite3.connect(DB)

    con.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            news_id TEXT UNIQUE,
            title TEXT NOT NULL,
            url TEXT NOT NULL,
            source TEXT,
            category TEXT,
            published_at TEXT,
            image TEXT,
            summary TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    con.execute("""
        CREATE INDEX IF NOT EXISTS idx_news_published
        ON news(published_at DESC)
    """)

    con.close()


def clean(text):
    if not text:
        return ""

    text = html.unescape(text)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_date(value):
    if not value:
        return None

    try:
        return parsedate_to_datetime(value).isoformat()
    except Exception:
        return value


def detect_category(title, description):
    text = f"{title} {description}".lower()

    for keyword, category in CATEGORIES.items():
        if keyword in text:
            return category

    return "general"


def fetch_feed(source, feed_url):
    request = urllib.request.Request(
        feed_url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    with urllib.request.urlopen(request, timeout=15) as response:
        data = response.read()

    root = ET.fromstring(data)
    articles = []

    for item in root.findall(".//item"):
        title = clean(item.findtext("title"))
        url = clean(item.findtext("link"))
        description = clean(item.findtext("description"))
        published_at = parse_date(item.findtext("pubDate"))

        if not title or not url:
            continue

        news_id = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()

        articles.append({
            "news_id": news_id,
            "title": title,
            "url": url,
            "source": source,
            "category": detect_category(
                title,
                description
            ),
            "published_at": published_at,
            "image": None,
            "summary": description[:1000]
        })

    return articles


def save_news(articles):
    if not articles:
        return 0

    con = sqlite3.connect(DB)
    count = 0

    for article in articles:
        cursor = con.execute("""
            INSERT OR IGNORE INTO news (
                news_id,
                title,
                url,
                source,
                category,
                published_at,
                image,
                summary
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article["news_id"],
            article["title"],
            article["url"],
            article["source"],
            article["category"],
            article["published_at"],
            article["image"],
            article["summary"]
        ))

        count += cursor.rowcount

    con.commit()
    con.close()

    return count


def crawl_news():
    init_db()

    all_articles = []

    for source, feed_url in RSS_FEEDS.items():
        try:
            articles = fetch_feed(
                source,
                feed_url
            )

            all_articles.extend(articles)

            print(
                f"[NEWS] {source}: "
                f"{len(articles)} articles"
            )

        except Exception as error:
            print(
                f"[NEWS] {source} ERROR: "
                f"{error}"
            )

    new_count = save_news(all_articles)

    print(
        f"[NEWS] Total: {len(all_articles)} | "
        f"New: {new_count}"
    )

    return {
        "sources": len(RSS_FEEDS),
        "articles": len(all_articles),
        "new": new_count
    }


if __name__ == "__main__":
    print(crawl_news())