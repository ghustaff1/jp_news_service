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


@app.on_event("startup")
def create_table():
    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS news (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image_url TEXT,
            level VARCHAR(2) NOT NULL,
            source_url TEXT,
            published_at TIMESTAMP
        );
    """)

    connection.commit()
    cursor.close()
    connection.close()


@app.get("/")
def root():
    return {"message": "JP News API is working!"}


@app.get("/db")
def database_test():
    connection = get_connection()
    connection.close()

    return {"database": "connected"}
