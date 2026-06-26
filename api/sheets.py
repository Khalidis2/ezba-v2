# api/sheets.py

import json
import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")

S_OPERATIONS = "العمليات"
S_INVENTORY = "الجرد"
S_PEOPLE = "الأشخاص"
S_STATE = "الحالة"


def sheets_service():
    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(
        info,
        scopes=["https://www.googleapis.com/auth/spreadsheets"],
    )
    return build("sheets", "v4", credentials=creds)


def read_rows(svc, sheet, rng="A1:Z"):
    try:
        result = svc.spreadsheets().values().get(
            spreadsheetId=SPREADSHEET_ID,
            range=f"{sheet}!{rng}",
        ).execute()
        return result.get("values", [])
    except Exception:
        return []


def append_row(svc, sheet, row):
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()


def update_row(svc, sheet, row_number, row):
    end_col = chr(ord("A") + len(row) - 1)
    svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet}!A{row_number}:{end_col}{row_number}",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()


def rows_to_dicts(rows):
    if not rows:
        return []
    headers = rows[0]
    out = []
    for index, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        item = {headers[i]: row[i] if i < len(row) else "" for i in range(len(headers))}
        item["_row"] = index
        out.append(item)
    return out


def get_inventory(svc, active_only=True):
    rows = rows_to_dicts(read_rows(svc, S_INVENTORY))
    if active_only:
        rows = [x for x in rows if x.get("الحالة", "فعال") != "غير فعال"]
    return rows


def get_inventory_item(svc, item_id):
    for item in get_inventory(svc, active_only=False):
        if str(item.get("رقم الصنف", "")).strip() == str(item_id):
            return item
    return None


def update_inventory_qty(svc, item_id, delta):
    item = get_inventory_item(svc, item_id)
    if not item:
        return
    try:
        current = float(item.get("الكمية الحالية") or 0)
    except Exception:
        current = 0
    new_qty = current + float(delta)
    row = [
        item.get("رقم الصنف", ""),
        item.get("التصنيف", ""),
        item.get("الصنف", ""),
        new_qty,
        item.get("الحد الأدنى", ""),
        item.get("الحالة", "فعال"),
        item.get("ملاحظات", ""),
    ]
    update_row(svc, S_INVENTORY, item["_row"], row)


def get_people(svc, person_type=None, active_only=True):
    rows = rows_to_dicts(read_rows(svc, S_PEOPLE))
    if active_only:
        rows = [x for x in rows if x.get("الحالة", "فعال") != "غير فعال"]
    if person_type:
        rows = [x for x in rows if x.get("النوع") == person_type]
    return rows


def get_person(svc, person_id):
    for person in get_people(svc, active_only=False):
        if str(person.get("رقم الشخص", "")).strip() == str(person_id):
            return person
    return None


def next_person_id(svc):
    rows = get_people(svc, active_only=False)
    numbers = []
    for row in rows:
        try:
            numbers.append(int(row.get("رقم الشخص") or 0))
        except Exception:
            pass
    return str(max(numbers or [0]) + 1)


def add_person(svc, name, person_type):
    person_id = next_person_id(svc)
    append_row(svc, S_PEOPLE, [person_id, name, person_type, "فعال", ""])
    return {"رقم الشخص": person_id, "الاسم": name, "النوع": person_type, "الحالة": "فعال", "ملاحظات": ""}


def add_operation(svc, row):
    append_row(svc, S_OPERATIONS, row)


def get_operations(svc):
    return rows_to_dicts(read_rows(svc, S_OPERATIONS))
