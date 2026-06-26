# app/data.py

from app.config import SHEET_INVENTORY, SHEET_PEOPLE, SHEET_OPERATIONS
from app.sheets import get_records, append_row, update_row
from app.utils import new_operation_id, now_str, safe_float


def active_inventory():
    return [x for x in get_records(SHEET_INVENTORY) if x.get("الحالة", "فعال") == "فعال"]


def find_inventory_by_id(item_id):
    for item in active_inventory():
        if str(item.get("رقم الصنف")) == str(item_id):
            return item
    return None


def active_people(person_type=None):
    people = [x for x in get_records(SHEET_PEOPLE) if x.get("الحالة", "فعال") == "فعال"]
    if person_type:
        people = [x for x in people if x.get("النوع") == person_type]
    return people


def find_person_by_id(person_id):
    for person in get_records(SHEET_PEOPLE):
        if str(person.get("رقم الشخص")) == str(person_id):
            return person
    return None


def add_person(name, person_type):
    records = get_records(SHEET_PEOPLE)
    next_id = str(len(records) + 1)
    append_row(SHEET_PEOPLE, [next_id, name, person_type, "فعال", ""])
    return name


def add_operation(data, user_name):
    row = [
        new_operation_id(),
        now_str(),
        data.get("العملية", ""),
        data.get("التصنيف", ""),
        data.get("الصنف", ""),
        data.get("الكمية", ""),
        data.get("الإجمالي", ""),
        data.get("طريقة الدفع", ""),
        data.get("حالة الدفع", ""),
        data.get("الطرف", ""),
        user_name,
        data.get("ملاحظات", ""),
    ]
    append_row(SHEET_OPERATIONS, row)
    return row[0]


def update_inventory_quantity(item_name, delta):
    records = get_records(SHEET_INVENTORY)
    for item in records:
        if item.get("الصنف") == item_name:
            current = safe_float(item.get("الكمية الحالية", 0))
            updated = current + safe_float(delta)
            values = [
                item.get("رقم الصنف", ""),
                item.get("التصنيف", ""),
                item.get("الصنف", ""),
                updated,
                item.get("الحد الأدنى", ""),
                item.get("الحالة", "فعال"),
                item.get("ملاحظات", ""),
            ]
            update_row(SHEET_INVENTORY, item["_row"], values)
            return


def operations():
    return get_records(SHEET_OPERATIONS)
