from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def root():
    return {"message": "JP News API is working!"}
