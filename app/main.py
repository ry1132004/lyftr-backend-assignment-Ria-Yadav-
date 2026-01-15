from fastapi import FastAPI
from app.models import init_db
from fastapi import Response, status
from app.config import WEBHOOK_SECRET
from app.models import get_connection
from app.logging_utils import log_request
import hmac
from app.storage import list_messages
import hashlib
from fastapi import Request, Header, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from app.storage import insert_message
from app.config import WEBHOOK_SECRET

class WebhookMessage(BaseModel):
    message_id: str = Field(..., min_length=1)
    from_: str = Field(..., alias="from")
    to: str
    ts: str
    text: Optional[str] = Field(None, max_length=4096)


app = FastAPI()

app.middleware("http")(log_request)


@app.on_event("startup")
def startup():
    init_db()

@app.get("/health/live")
def live():
    return {"status": "live"}

@app.get("/health/ready")
def ready(response: Response):
    if not WEBHOOK_SECRET:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready"}

    try:
        conn = get_connection()
        conn.execute("SELECT 1")
        conn.close()
    except Exception:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not ready"}

    return {"status": "ready"}

@app.post("/webhook")
async def webhook(
    request: Request,
    payload: WebhookMessage,
    x_signature: str = Header(None)
):
    raw_body = await request.body()

    if not x_signature:
        raise HTTPException(status_code=401, detail="invalid signature")

    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, x_signature):
        raise HTTPException(status_code=401, detail="invalid signature")

    inserted = insert_message(payload.dict(by_alias=True))

    return {"status": "ok"}



@app.post("/test-webhook")
def test():
    return {"test": "ok"}


@app.get("/messages")
def get_messages(limit: int = 50, offset: int = 0):
    rows = list_messages(limit, offset)
    return {
        "data": [
            {
                "message_id": r[0],
                "from": r[1],
                "to": r[2],
                "ts": r[3],
                "text": r[4]
            } for r in rows
        ],
        "limit": limit,
        "offset": offset
    }

from app.storage import get_stats

@app.get("/stats")
def stats():
    return get_stats()
