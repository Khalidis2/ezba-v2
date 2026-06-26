# api/state.py

from sheets import read_rows, rows_to_dicts, update_row, append_row, S_STATE
from utils import now_str, safe_json_loads, safe_json_dumps


def get_state(svc, user_id):
    rows = rows_to_dicts(read_rows(svc, S_STATE))
    for row in rows:
        if str(row.get("رقم المستخدم", "")).strip() == str(user_id):
            data = safe_json_loads(row.get("البيانات", ""), {})
            return {
                "row": row.get("_row"),
                "user_id": str(user_id),
                "user_name": row.get("اسم المستخدم", ""),
                "stage": row.get("المرحلة الحالية", ""),
                "data": data,
            }
    return {"row": None, "user_id": str(user_id), "user_name": "", "stage": "", "data": {}}


def set_state(svc, user_id, user_name, stage, data=None):
    current = get_state(svc, user_id)
    row = [str(user_id), user_name, stage, safe_json_dumps(data or {}), now_str()]
    if current.get("row"):
        update_row(svc, S_STATE, current["row"], row)
    else:
        append_row(svc, S_STATE, row)


def clear_state(svc, user_id, user_name=""):
    set_state(svc, user_id, user_name, "", {})
