# app/telegram_client.py

import requests
from app.config import TELEGRAM_BOT_TOKEN

BASE_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"


def send_message(chat_id, text, reply_markup=None):
    if not TELEGRAM_BOT_TOKEN:
        return
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/sendMessage", json=payload, timeout=15)


def edit_message(chat_id, message_id, text, reply_markup=None):
    if not TELEGRAM_BOT_TOKEN:
        return
    payload = {"chat_id": chat_id, "message_id": message_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    requests.post(f"{BASE_URL}/editMessageText", json=payload, timeout=15)


def answer_callback(callback_id, text=""):
    if not TELEGRAM_BOT_TOKEN:
        return
    requests.post(f"{BASE_URL}/answerCallbackQuery", json={"callback_query_id": callback_id, "text": text}, timeout=15)
