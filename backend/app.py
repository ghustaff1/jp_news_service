import os

import psycopg2
from fastapi import FastAPI

app = FastAPI()


def get_connection():
    return psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )


@app.get("/")
def root():
    return {"message": "JP News API is working!"}


@app.get("/news")
def get_news(level: str | None = None):
    connection = get_connection()
    cursor = connection.cursor()

    if level:
        cursor.execute(
            """
            SELECT id, title, content, image_url, level, source_url
            FROM news
            WHERE level = %s
            ORDER BY id DESC
            """,
            (level,),
        )
    else:
        cursor.execute(
            """
            SELECT id, title, content, image_url, level, source_url
            FROM news
            ORDER BY id DESC
            """
        )

    rows = cursor.fetchall()

    cursor.close()
    connection.close()

    return [
        {
            "id": row[0],
            "title": row[1],
            "content": row[2],
            "image_url": row[3],
            "level": row[4],
            "source_url": row[5],
        }
        for row in rows
    ]
