# app/utils.py

from datetime import datetime, timezone, timedelta
import json
import uuid

UAE_TZ = timezone(timedelta(hours=4))


def now_str():
    return datetime.now(UAE_TZ).strftime("%Y-%m-%d %H:%M:%S")


def new_operation_id():
    return "EZ-" + uuid.uuid4().hex[:8].upper()


def fmt_amount(value):
    try:
        num = float(value)
        return str(int(num)) if num.is_integer() else str(round(num, 2))
    except Exception:
        return str(value)


def safe_float(value):
    try:
        return float(str(value).replace(",", "."))
    except Exception:
        return 0.0


def encode_json(data):
    return json.dumps(data or {}, ensure_ascii=False)


def decode_json(value):
    try:
        return json.loads(value or "{}")
    except Exception:
        return {}
