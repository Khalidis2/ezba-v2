# app/keyboards.py


def button(text, data):
    return {"text": text, "callback_data": data}


def keyboard(rows):
    return {"inline_keyboard": rows}


def main_menu():
    return keyboard([
        [button("➕ عملية جديدة", "new")],
        [button("📦 الجرد", "inventory"), button("📊 التقارير", "reports")],
        [button("👥 الأشخاص", "people")],
    ])


def operation_menu():
    return keyboard([
        [button("💰 بيع", "op:sell"), button("🛒 شراء", "op:buy")],
        [button("💸 مصروف", "op:expense")],
        [button("⬅️ رجوع", "home")],
    ])


def items_menu(items, prefix):
    rows = []
    row = []
    for item in items[:30]:
        row.append(button(item["الصنف"], f"{prefix}:{item['رقم الصنف']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([button("➕ أخرى", f"{prefix}:other")])
    rows.append([button("⬅️ رجوع", "new"), button("🏠 الرئيسية", "home")])
    return keyboard(rows)


def expense_menu():
    return keyboard([
        [button("⚡ كهرباء", "expense:كهرباء"), button("💧 ماء", "expense:ماء")],
        [button("👷 رواتب", "expense:راتب"), button("🌾 علف", "expense:علف")],
        [button("💊 علاج", "expense:علاج"), button("🔧 صيانة", "expense:صيانة")],
        [button("🚚 نقل", "expense:نقل"), button("📦 أخرى", "expense:other")],
        [button("⬅️ رجوع", "new"), button("🏠 الرئيسية", "home")],
    ])


def payment_menu():
    return keyboard([
        [button("💵 كاش", "pay:كاش"), button("🏦 تحويل", "pay:تحويل")],
        [button("📒 آجل", "pay:آجل")],
        [button("❌ إلغاء", "cancel")],
    ])


def payment_status_menu():
    return keyboard([
        [button("✅ مدفوع", "pstatus:مدفوع")],
        [button("⏳ غير مدفوع", "pstatus:غير مدفوع")],
        [button("➗ مدفوع جزئياً", "pstatus:مدفوع جزئياً")],
        [button("❌ إلغاء", "cancel")],
    ])


def people_menu(people, prefix, allow_none=True):
    rows = []
    row = []
    for person in people[:30]:
        row.append(button(person["الاسم"], f"{prefix}:{person['رقم الشخص']}"))
        if len(row) == 2:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    if allow_none:
        rows.append([button("بدون", f"{prefix}:none")])
    rows.append([button("➕ جديد", f"{prefix}:new")])
    rows.append([button("❌ إلغاء", "cancel")])
    return keyboard(rows)


def note_menu():
    return keyboard([
        [button("بدون ملاحظات", "note:none")],
        [button("✍️ كتابة ملاحظة", "note:write")],
        [button("❌ إلغاء", "cancel")],
    ])


def confirm_menu():
    return keyboard([
        [button("✅ تأكيد", "confirm"), button("❌ إلغاء", "cancel")],
        [button("🏠 الرئيسية", "home")],
    ])


def reports_menu():
    return keyboard([
        [button("اليوم", "report:today"), button("الشهر", "report:month")],
        [button("آخر العمليات", "report:last")],
        [button("🏠 الرئيسية", "home")],
    ])
