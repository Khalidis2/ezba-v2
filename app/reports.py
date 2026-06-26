# app/reports.py

from datetime import datetime
from app.data import operations, active_inventory
from app.utils import safe_float, fmt_amount


def report_last():
    rows = operations()[-8:]
    if not rows:
        return "لا توجد عمليات حتى الآن."
    lines = ["🕐 آخر العمليات"]
    for row in reversed(rows):
        op = row.get("العملية", "")
        item = row.get("الصنف", "")
        total = fmt_amount(row.get("الإجمالي", ""))
        lines.append(f"{row.get('التاريخ والوقت', '')[:10]} | {op} | {item} | {total} درهم")
    return "\n".join(lines)


def report_period(period):
    now = datetime.now()
    rows = operations()
    filtered = []
    for row in rows:
        dt = row.get("التاريخ والوقت", "")
        if period == "today" and dt.startswith(now.strftime("%Y-%m-%d")):
            filtered.append(row)
        elif period == "month" and dt.startswith(now.strftime("%Y-%m")):
            filtered.append(row)
    income = sum(safe_float(x.get("الإجمالي", 0)) for x in filtered if x.get("العملية") == "بيع")
    expense = sum(safe_float(x.get("الإجمالي", 0)) for x in filtered if x.get("العملية") != "بيع")
    label = "اليوم" if period == "today" else "هذا الشهر"
    return f"📊 تقرير {label}\nالدخل: {fmt_amount(income)} درهم\nالمصروف: {fmt_amount(expense)} درهم\nالصافي: {fmt_amount(income - expense)} درهم"


def inventory_report():
    items = active_inventory()
    if not items:
        return "📦 الجرد فارغ."
    lines = ["📦 الجرد الحالي"]
    for item in items:
        lines.append(f"{item.get('الصنف', '')}: {item.get('الكمية الحالية', '')}")
    return "\n".join(lines)
