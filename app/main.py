from fastapi import FastAPI
from app.models import init_db

app = FastAPI()

@app.on_event("startup")
def startup():
    init_db()

@app.get("/health/live")
def live():
    return {"status": "live"}
