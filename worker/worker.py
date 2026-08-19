import os
import time

import feedparser
import psycopg2
import requests
from bs4 import BeautifulSoup


RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"


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
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    description = ""
    image_url = ""

    og_title = soup.find("meta", property="og:title")
    og_description = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")

    if og_title:
        title = og_title.get("content", "")

    if og_description:
        description = og_description.get("content", "")

    if og_image:
        image_url = og_image.get("content", "")

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


def fetch_news():
    feed = feedparser.parse(RSS_URL)

    connection = get_connection()
    cursor = connection.cursor()

    for item in feed.entries[:10]:
        url = item.get("link")

        if not url:
            continue

        # Не добавляем одну и ту же новость повторно
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
                INSERT INTO news
                (title, content, image_url, level, source_url, published_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    title,
                    content,
                    image_url,
                    "N3",
                    url,
                    item.get("published"),
                ),
            )

            print(f"Added: {title}", flush=True)

        except Exception as e:
            print(f"Failed to parse {url}: {e}", flush=True)

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    while True:
        try:
            fetch_news()
            print("News fetch completed", flush=True)
        except Exception as e:
            print(f"Worker error: {e}", flush=True)

        time.sleep(3600)
