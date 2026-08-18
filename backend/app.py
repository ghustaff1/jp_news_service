import os

import psycopg2
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "JP News API is working!"}


@app.get("/db")
def database_test():
    connection = psycopg2.connect(
        host="db",
        database=os.getenv("POSTGRES_DB"),
        user=os.getenv("POSTGRES_USER"),
        password=os.getenv("POSTGRES_PASSWORD"),
    )

    connection.close()

    return {"database": "connected"}
