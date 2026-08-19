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
<<<<<<< HEAD
        headers={"User-Agent": "Mozilla/5.0"},
=======
        headers={
            "User-Agent": "Mozilla/5.0"
        },
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    title = ""
    description = ""
    image_url = ""

<<<<<<< HEAD
    meta = soup.find("meta", property="og:title")
    if meta:
        title = meta.get("content", "")

    meta = soup.find("meta", property="og:description")
    if meta:
        description = meta.get("content", "")

    meta = soup.find("meta", property="og:image")
    if meta:
        image_url = meta.get("content", "")
=======
    og_title = soup.find("meta", property="og:title")
    og_description = soup.find("meta", property="og:description")
    og_image = soup.find("meta", property="og:image")

    if og_title:
        title = og_title.get("content", "")

    if og_description:
        description = og_description.get("content", "")

    if og_image:
        image_url = og_image.get("content", "")
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621

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


<<<<<<< HEAD
def process_source(source):
    print(
        f"Fetching {source['name']} [{source['level']}]...",
        flush=True,
    )

    feed = feedparser.parse(source["url"])
=======
def fetch_news():
    feed = feedparser.parse(RSS_URL)
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621

    connection = get_connection()
    cursor = connection.cursor()

<<<<<<< HEAD
    for item in feed.entries[:source["limit"]]:

        url = item.get("link")

        if not url:
            continue
=======
    for item in feed.entries[:10]:
        url = item.get("link")
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621

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
<<<<<<< HEAD
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
=======
                INSERT INTO news
                (title, content, image_url, level, source_url, published_at)
                VALUES (%s, %s, %s, %s, %s, %s)
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621
                """,
                (
                    title,
                    content,
                    image_url,
<<<<<<< HEAD
                    source["level"],
                    url,
                    source["name"],
=======
                    "N3",
                    url,
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621
                    item.get("published"),
                ),
            )

<<<<<<< HEAD
            print(
                f"[{source['level']}] {title}",
                flush=True,
            )

        except Exception as e:
            print(
                f"Failed to parse {url}: {e}",
                flush=True,
            )
=======
            print(f"Added: {title}", flush=True)

        except Exception as e:
            print(f"Failed to parse {url}: {e}", flush=True)
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621

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
<<<<<<< HEAD
        fetch_news()

        print(
            "News fetch completed",
            flush=True,
        )
=======
        try:
            fetch_news()
            print("News fetch completed", flush=True)
        except Exception as e:
            print(f"Worker error: {e}", flush=True)
>>>>>>> 8832bf12a33580cebcf07fcf686427cc087bd621

        time.sleep(3600)
