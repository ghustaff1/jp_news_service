import os
import time

import feedparser
import psycopg2


RSS_URL = "https://www3.nhk.or.jp/rss/news/cat0.xml"


def get_connection():
    return psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


def fetch_news():
    feed = feedparser.parse(RSS_URL)

    connection = get_connection()
    cursor = connection.cursor()

    for item in feed.entries[:10]:
        title = item.get("title", "")
        url = item.get("link", "")

        cursor.execute(
            """
            INSERT INTO news (title, content, image_url, level, source_url)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                title,
                title,
                None,
                "N3",
                url,
            ),
        )

    connection.commit()
    cursor.close()
    connection.close()


if __name__ == "__main__":
    while True:
        try:
            fetch_news()
            print("News fetched successfully")
        except Exception as e:
            print(f"Worker error: {e}")

        time.sleep(3600)
