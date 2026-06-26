# app/state.py

from app.config import SHEET_STATE
from app.sheets import get_records, append_row, update_row
from app.utils import now_str, encode_json, decode_json


def get_state(user_id):
    records = get_records(SHEET_STATE)
    for record in records:
        if str(record.get("رقم المستخدم")) == str(user_id):
            return {
                "row": record["_row"],
                "user_id": record.get("رقم المستخدم", ""),
                "user_name": record.get("اسم المستخدم", ""),
                "stage": record.get("المرحلة الحالية", ""),
                "data": decode_json(record.get("البيانات", "")),
                "updated_at": record.get("آخر تحديث", ""),
            }
    return {"row": None, "stage": "", "data": {}}


def set_state(user_id, user_name, stage, data=None):
    current = get_state(user_id)
    row = [str(user_id), user_name, stage, encode_json(data or {}), now_str()]
    if current.get("row"):
        update_row(SHEET_STATE, current["row"], row)
    else:
        append_row(SHEET_STATE, row)


def clear_state(user_id, user_name=""):
    set_state(user_id, user_name, "", {})
