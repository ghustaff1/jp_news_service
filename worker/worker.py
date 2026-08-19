import os
import time

import feedparser
import psycopg2
import requests
from bs4 import BeautifulSoup


SOURCES = [
    {
        "name": "NHK Easy",
        "url": "https://nhkeasier.com/feed/",
        "level": "N4",
        "limit": 10,
    },
    {
        "name": "NHK News",
        "url": "https://www3.nhk.or.jp/rss/news/cat0.xml",
        "level": "N3",
        "limit": 5,
    },
    {
        "name": "NHK News",
        "url": "https://www3.nhk.or.jp/rss/news/cat1.xml",
        "level": "N2",
        "limit": 5,
    },
]


def get_connection():
    return psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def parse_article(url):
    response = requests.get(
        url,
        timeout=15,
        headers={"User-Agent": "Mozilla/5.0"},
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    description = ""
    image_url = ""

    meta = soup.find("meta", property="og:title")
    if meta:
        title = meta.get("content", "")

    meta = soup.find("meta", property="og:description")
    if meta:
        description = meta.get("content", "")

    meta = soup.find("meta", property="og:image")
    if meta:
        image_url = meta.get("content", "")

    article = soup.find("article")

    if article:
        paragraphs = article.find_all("p")
        content = "\n".join(
            p.get_text(" ", strip=True)
            for p in paragraphs
            if p.get_text(strip=True)
        )
    else:
        content = description

    return title, content, image_url


def process_source(source):
    print(
        f"Fetching {source['name']} [{source['level']}]...",
        flush=True,
    )

    feed = feedparser.parse(source["url"])

    connection = get_connection()
    cursor = connection.cursor()

    for item in feed.entries[:source["limit"]]:

        url = item.get("link")

        if not url:
            continue

        cursor.execute(
            "SELECT id FROM news WHERE source_url = %s",
            (url,),
        )

        if cursor.fetchone():
            continue

        try:
            title, content, image_url = parse_article(url)

            if not title:
                title = item.get("title", "")

            cursor.execute(
                """
                INSERT INTO news (
                    title,
                    content,
                    image_url,
                    level,
                    source_url,
                    source,
                    published_at
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    title,
                    content,
                    image_url,
                    source["level"],
                    url,
                    source["name"],
                    item.get("published"),
                ),
            )

            print(
                f"[{source['level']}] {title}",
                flush=True,
            )

        except Exception as e:
            print(
                f"Failed to parse {url}: {e}",
                flush=True,
            )

    connection.commit()
    cursor.close()
    connection.close()


def fetch_news():
    for source in SOURCES:
        try:
            process_source(source)
        except Exception as e:
            print(
                f"Source error "
                f"({source['name']} / {source['level']}): {e}",
                flush=True,
            )


if __name__ == "__main__":
    while True:
        fetch_news()

        print(
            "News fetch completed",
            flush=True,
        )

        time.sleep(3600)
