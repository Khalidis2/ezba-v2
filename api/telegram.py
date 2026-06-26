# api/telegram.py

from fastapi import FastAPI, Request
from app.flows import handle_callback, handle_text

app = FastAPI()


@app.get("/")
def root():
    return {"ok": True, "service": "Ezba V2"}


@app.get("/api/telegram")
def health():
    return {"ok": True}


@app.get("/api/telegram-webhook")
def health_legacy():
    return {"ok": True}


@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    update = await request.json()
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_text(update["message"])
    return {"ok": True}


@app.post("/api/telegram-webhook")
async def telegram_webhook_legacy(request: Request):
    update = await request.json()
    if "callback_query" in update:
        handle_callback(update["callback_query"])
    elif "message" in update:
        handle_text(update["message"])
    return {"ok": True}
