# api/utils.py

from datetime import datetime, timezone, timedelta
import json
import os
import re
import uuid

UAE_TZ = timezone(timedelta(hours=4))

ALLOWED_USERS = {
    47329648: "Khaled",
    6894180427: "Hamad",
}


def now_str():
    return datetime.now(UAE_TZ).strftime("%Y-%m-%d %H:%M")


def today_key():
    return datetime.now(UAE_TZ).strftime("%Y-%m-%d")


def month_key():
    return datetime.now(UAE_TZ).strftime("%Y-%m")


def new_operation_id():
    return "EZ-" + datetime.now(UAE_TZ).strftime("%y%m%d-%H%M%S-") + uuid.uuid4().hex[:4].upper()


def fmt_number(value):
    try:
        number = float(value)
        return str(int(number)) if number.is_integer() else str(round(number, 2))
    except Exception:
        return str(value)


def parse_number(text):
    text = str(text or "").strip()
    text = text.translate(str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789"))
    text = text.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789"))
    text = text.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return None
    return float(match.group(0))


def is_allowed_user(user_id):
    raw = os.environ.get("ALLOWED_USERS", "").strip()
    if raw:
        allowed = {int(x.strip()) for x in raw.split(",") if x.strip().isdigit()}
        return int(user_id) in allowed
    return int(user_id) in ALLOWED_USERS


def user_display_name(user_id, telegram_user=None):
    if int(user_id) in ALLOWED_USERS:
        return ALLOWED_USERS[int(user_id)]
    if telegram_user:
        return telegram_user.get("first_name") or telegram_user.get("username") or str(user_id)
    return str(user_id)


def safe_json_loads(value, default=None):
    try:
        return json.loads(value) if value else (default or {})
    except Exception:
        return default or {}


def safe_json_dumps(value):
    return json.dumps(value or {}, ensure_ascii=False)


def normalize_status(value):
    return str(value or "").strip()
