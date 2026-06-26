# api/telegram-webhook.py

from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import requests

sys.path.append(os.path.dirname(__file__))

from keyboards import main_menu, operation_menu, inventory_items, expense_menu, payment_menu, payment_status_menu, people_menu, notes_menu, confirm_menu, reports_menu
from sheets import sheets_service, get_inventory, get_inventory_item, update_inventory_qty, get_people, get_person, add_person, add_operation, get_operations
from state import get_state, set_state, clear_state
from utils import is_allowed_user, user_display_name, parse_number, fmt_number, now_str, today_key, month_key, new_operation_id

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
D = "──────────────"


def telegram(method, payload):
    if not TELEGRAM_BOT_TOKEN:
        return
    try:
        requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}", json=payload, timeout=15)
    except Exception:
        pass


def send(chat_id, text, reply_markup=None):
    payload = {"chat_id": chat_id, "text": text}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    telegram("sendMessage", payload)


def answer_callback(callback_id):
    telegram("answerCallbackQuery", {"callback_query_id": callback_id})


def show_home(chat_id, svc, user_id, user_name):
    clear_state(svc, user_id, user_name)
    send(chat_id, "🏠 القائمة الرئيسية", main_menu())


def ask_quantity(chat_id, svc, user_id, user_name, data):
    set_state(svc, user_id, user_name, "انتظار_الكمية", data)
    item = data.get("الصنف", "الصنف")
    send(chat_id, f"اكتب الكمية لـ {item}:")


def ask_total(chat_id, svc, user_id, user_name, data):
    set_state(svc, user_id, user_name, "انتظار_الإجمالي", data)
    send(chat_id, "اكتب الإجمالي بالدرهم:")


def ask_party(chat_id, svc, user_id, user_name, data):
    operation = data.get("العملية")
    if operation == "بيع":
        people = get_people(svc, "عميل")
        title = "اختر العميل:"
    elif operation == "شراء":
        people = get_people(svc, "مورد")
        title = "اختر المورد:"
    elif data.get("الصنف") == "راتب":
        people = get_people(svc, "عامل")
        title = "اختر العامل:"
    else:
        people = get_people(svc)
        title = "اختر الطرف:"
    set_state(svc, user_id, user_name, "انتظار_الطرف", data)
    send(chat_id, title, people_menu(people))


def ask_notes(chat_id, svc, user_id, user_name, data):
    set_state(svc, user_id, user_name, "انتظار_الملاحظات", data)
    send(chat_id, "هل توجد ملاحظات؟", notes_menu())


def show_confirm(chat_id, svc, user_id, user_name, data):
    set_state(svc, user_id, user_name, "انتظار_التأكيد", data)
    text = (
        f"{D}\n"
        f"راجع العملية:\n"
        f"العملية: {data.get('العملية', '')}\n"
        f"التصنيف: {data.get('التصنيف', '')}\n"
        f"الصنف: {data.get('الصنف', '')}\n"
        f"الكمية: {fmt_number(data.get('الكمية', 0))}\n"
        f"الإجمالي: {fmt_number(data.get('الإجمالي', 0))} درهم\n"
        f"طريقة الدفع: {data.get('طريقة الدفع', '')}\n"
        f"حالة الدفع: {data.get('حالة الدفع', '')}\n"
        f"الطرف: {data.get('الطرف', '') or '-'}\n"
        f"الملاحظات: {data.get('ملاحظات', '') or '-'}\n"
        f"{D}"
    )
    send(chat_id, text, confirm_menu())


def save_operation(chat_id, svc, user_id, user_name, data):
    op_id = new_operation_id()
    row = [
        op_id,
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
    add_operation(svc, row)
    if data.get("رقم الصنف"):
        if data.get("العملية") == "بيع":
            update_inventory_qty(svc, data.get("رقم الصنف"), -float(data.get("الكمية") or 0))
        elif data.get("العملية") == "شراء":
            update_inventory_qty(svc, data.get("رقم الصنف"), float(data.get("الكمية") or 0))
    clear_state(svc, user_id, user_name)
    send(chat_id, f"✅ تم حفظ العملية\nرقم العملية: {op_id}", main_menu())


def handle_callback(chat_id, user_id, user_name, svc, data, callback_id):
    answer_callback(callback_id)
    state = get_state(svc, user_id)
    payload = state.get("data", {})

    if data == "cancel" or data == "confirm:no":
        clear_state(svc, user_id, user_name)
        send(chat_id, "تم الإلغاء.", main_menu())
        return

    if data == "main:home":
        show_home(chat_id, svc, user_id, user_name)
        return

    if data == "main:new":
        set_state(svc, user_id, user_name, "اختيار_العملية", {})
        send(chat_id, "اختر نوع العملية:", operation_menu())
        return

    if data == "main:inventory":
        items = get_inventory(svc)
        lines = [D, "📦 الجرد"]
        for item in items[:40]:
            lines.append(f"{item.get('الصنف', '')}: {fmt_number(item.get('الكمية الحالية', 0))}")
        lines.append(D)
        send(chat_id, "\n".join(lines), main_menu())
        return

    if data == "main:reports":
        send(chat_id, "اختر التقرير:", reports_menu())
        return

    if data.startswith("rep:"):
        period = data.split(":", 1)[1]
        show_report(chat_id, svc, period)
        return

    if data == "op:sale" or data == "op:buy":
        operation = "بيع" if data == "op:sale" else "شراء"
        set_state(svc, user_id, user_name, "اختيار_الصنف", {"العملية": operation})
        send(chat_id, "اختر الصنف:", inventory_items(get_inventory(svc)))
        return

    if data == "op:expense":
        set_state(svc, user_id, user_name, "اختيار_المصروف", {"العملية": "مصروف", "الكمية": 1})
        send(chat_id, "اختر نوع المصروف:", expense_menu())
        return

    if data.startswith("exp:"):
        item = data.split(":", 1)[1]
        payload = {"العملية": "مصروف", "التصنيف": "مصروفات", "الصنف": item, "الكمية": 1}
        if item == "أخرى":
            set_state(svc, user_id, user_name, "انتظار_مصروف_آخر", payload)
            send(chat_id, "اكتب اسم المصروف:")
        else:
            ask_total(chat_id, svc, user_id, user_name, payload)
        return

    if data.startswith("item:"):
        item_id = data.split(":", 1)[1]
        if item_id == "custom":
            payload["رقم الصنف"] = ""
            set_state(svc, user_id, user_name, "انتظار_صنف_آخر", payload)
            send(chat_id, "اكتب اسم الصنف:")
            return
        item = get_inventory_item(svc, item_id)
        if not item:
            send(chat_id, "الصنف غير موجود.", main_menu())
            return
        payload.update({
            "رقم الصنف": item.get("رقم الصنف", ""),
            "التصنيف": item.get("التصنيف", ""),
            "الصنف": item.get("الصنف", ""),
        })
        ask_quantity(chat_id, svc, user_id, user_name, payload)
        return

    if data.startswith("pay:"):
        payment = data.split(":", 1)[1]
        payload["طريقة الدفع"] = payment
        set_state(svc, user_id, user_name, "انتظار_حالة_الدفع", payload)
        send(chat_id, "اختر حالة الدفع:", payment_status_menu(payment))
        return

    if data.startswith("pstat:"):
        payload["حالة الدفع"] = data.split(":", 1)[1]
        ask_party(chat_id, svc, user_id, user_name, payload)
        return

    if data.startswith("party:"):
        person_id = data.split(":", 1)[1]
        if person_id == "none":
            payload["الطرف"] = ""
            ask_notes(chat_id, svc, user_id, user_name, payload)
            return
        if person_id == "new":
            set_state(svc, user_id, user_name, "انتظار_طرف_جديد", payload)
            send(chat_id, "اكتب الاسم:")
            return
        person = get_person(svc, person_id)
        payload["الطرف"] = person.get("الاسم", "") if person else ""
        ask_notes(chat_id, svc, user_id, user_name, payload)
        return

    if data == "note:none":
        payload["ملاحظات"] = ""
        show_confirm(chat_id, svc, user_id, user_name, payload)
        return

    if data == "note:write":
        set_state(svc, user_id, user_name, "انتظار_ملاحظة_نص", payload)
        send(chat_id, "اكتب الملاحظة:")
        return

    if data == "confirm:yes":
        save_operation(chat_id, svc, user_id, user_name, payload)
        return

    send(chat_id, "أمر غير معروف.", main_menu())


def handle_text(chat_id, user_id, user_name, svc, text):
    if text in ("/start", "/menu", "القائمة", "الرئيسية"):
        show_home(chat_id, svc, user_id, user_name)
        return

    state = get_state(svc, user_id)
    stage = state.get("stage", "")
    data = state.get("data", {})

    if stage == "انتظار_صنف_آخر":
        data["الصنف"] = text.strip()
        data["التصنيف"] = "أخرى"
        ask_quantity(chat_id, svc, user_id, user_name, data)
        return

    if stage == "انتظار_مصروف_آخر":
        data["الصنف"] = text.strip()
        ask_total(chat_id, svc, user_id, user_name, data)
        return

    if stage == "انتظار_الكمية":
        number = parse_number(text)
        if number is None or number <= 0:
            send(chat_id, "اكتب رقم صحيح للكمية.")
            return
        data["الكمية"] = number
        ask_total(chat_id, svc, user_id, user_name, data)
        return

    if stage == "انتظار_الإجمالي":
        number = parse_number(text)
        if number is None or number < 0:
            send(chat_id, "اكتب رقم صحيح للإجمالي.")
            return
        data["الإجمالي"] = number
        set_state(svc, user_id, user_name, "انتظار_طريقة_الدفع", data)
        send(chat_id, "اختر طريقة الدفع:", payment_menu())
        return

    if stage == "انتظار_طرف_جديد":
        operation = data.get("العملية")
        person_type = "عميل" if operation == "بيع" else "مورد"
        if data.get("الصنف") == "راتب":
            person_type = "عامل"
        person = add_person(svc, text.strip(), person_type)
        data["الطرف"] = person.get("الاسم", "")
        ask_notes(chat_id, svc, user_id, user_name, data)
        return

    if stage == "انتظار_ملاحظة_نص":
        data["ملاحظات"] = text.strip()
        show_confirm(chat_id, svc, user_id, user_name, data)
        return

    send(chat_id, "استخدم القائمة للبدء:", main_menu())


def show_report(chat_id, svc, period):
    rows = get_operations(svc)
    if period == "today":
        rows = [x for x in rows if str(x.get("التاريخ والوقت", "")).startswith(today_key())]
        label = "اليوم"
    elif period == "month":
        rows = [x for x in rows if str(x.get("التاريخ والوقت", "")).startswith(month_key())]
        label = "هذا الشهر"
    else:
        label = "كل العمليات"

    income = 0
    expense = 0
    for row in rows:
        try:
            total = float(row.get("الإجمالي") or 0)
        except Exception:
            total = 0
        if row.get("العملية") == "بيع":
            income += total
        else:
            expense += total

    net = income - expense
    send(chat_id, f"{D}\n📊 تقرير {label}\nالدخل: {fmt_number(income)} درهم\nالمصروف: {fmt_number(expense)} درهم\nالصافي: {fmt_number(net)} درهم\n{D}", main_menu())


class handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _ok(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self._ok()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            update = json.loads(raw)
        except Exception:
            self._ok()
            return

        message = update.get("message")
        callback = update.get("callback_query")

        if callback:
            msg = callback.get("message", {})
            chat_id = msg.get("chat", {}).get("id")
            from_user = callback.get("from", {})
            user_id = from_user.get("id")
            data = callback.get("data", "")
            callback_id = callback.get("id")
        elif message:
            chat_id = message.get("chat", {}).get("id")
            from_user = message.get("from", {})
            user_id = from_user.get("id")
            data = None
            callback_id = None
        else:
            self._ok()
            return

        if not user_id or not is_allowed_user(user_id):
            if chat_id:
                send(chat_id, "⛔ هذا البوت خاص")
            self._ok()
            return

        user_name = user_display_name(user_id, from_user)

        try:
            svc = sheets_service()
            if callback:
                handle_callback(chat_id, user_id, user_name, svc, data, callback_id)
            else:
                text = str(message.get("text") or "").strip()
                if text:
                    handle_text(chat_id, user_id, user_name, svc, text)
        except Exception as e:
            if chat_id:
                send(chat_id, f"صار خطأ:\n{e}")

        self._ok()
