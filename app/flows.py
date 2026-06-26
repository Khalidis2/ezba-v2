# app/flows.py

from app.config import ALLOWED_USERS
from app.telegram_client import send_message, edit_message, answer_callback
from app.keyboards import main_menu, operation_menu, items_menu, expense_menu, payment_menu, payment_status_menu, people_menu, note_menu, confirm_menu, reports_menu
from app.state import get_state, set_state, clear_state
from app.data import active_inventory, find_inventory_by_id, active_people, find_person_by_id, add_person, add_operation, update_inventory_quantity
from app.reports import report_last, report_period, inventory_report
from app.utils import safe_float, fmt_amount


def user_name(user_id):
    return ALLOWED_USERS.get(int(user_id), str(user_id))


def start(chat_id, user_id):
    clear_state(user_id, user_name(user_id))
    send_message(chat_id, "🏠 القائمة الرئيسية", main_menu())


def handle_callback(callback):
    callback_id = callback["id"]
    message = callback["message"]
    chat_id = message["chat"]["id"]
    message_id = message["message_id"]
    user_id = callback["from"]["id"]
    data = callback.get("data", "")
    name = user_name(user_id)
    answer_callback(callback_id)

    if user_id not in ALLOWED_USERS:
        edit_message(chat_id, message_id, "⛔ هذا البوت خاص")
        return

    if data in ["home", "cancel"]:
        clear_state(user_id, name)
        edit_message(chat_id, message_id, "🏠 القائمة الرئيسية", main_menu())
        return

    if data == "new":
        edit_message(chat_id, message_id, "اختر نوع العملية:", operation_menu())
        return

    if data == "inventory":
        edit_message(chat_id, message_id, inventory_report(), main_menu())
        return

    if data == "reports":
        edit_message(chat_id, message_id, "📊 اختر التقرير:", reports_menu())
        return

    if data.startswith("report:"):
        value = data.split(":", 1)[1]
        if value == "last":
            edit_message(chat_id, message_id, report_last(), reports_menu())
        else:
            edit_message(chat_id, message_id, report_period(value), reports_menu())
        return

    if data == "people":
        edit_message(chat_id, message_id, "👥 الأشخاص محفوظين في شيت الأشخاص. التعديل يكون من Google Sheets حالياً.", main_menu())
        return

    if data.startswith("op:"):
        op = data.split(":", 1)[1]
        if op == "expense":
            set_state(user_id, name, "اختيار_مصروف", {"العملية": "مصروف"})
            edit_message(chat_id, message_id, "💸 اختر نوع المصروف:", expense_menu())
            return
        operation = "بيع" if op == "sell" else "شراء"
        set_state(user_id, name, "اختيار_صنف", {"العملية": operation})
        edit_message(chat_id, message_id, "اختر الصنف:", items_menu(active_inventory(), "item"))
        return

    if data.startswith("item:"):
        item_id = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        if item_id == "other":
            set_state(user_id, name, "كتابة_صنف", payload)
            edit_message(chat_id, message_id, "اكتب اسم الصنف:")
            return
        item = find_inventory_by_id(item_id)
        if not item:
            edit_message(chat_id, message_id, "الصنف غير موجود. ارجع للقائمة الرئيسية.", main_menu())
            return
        payload.update({"التصنيف": item.get("التصنيف", ""), "الصنف": item.get("الصنف", "")})
        set_state(user_id, name, "انتظار_كمية", payload)
        edit_message(chat_id, message_id, f"اكتب الكمية لـ {item.get('الصنف')}:\nمثال: 5")
        return

    if data.startswith("expense:"):
        item = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        if item == "other":
            set_state(user_id, name, "كتابة_مصروف", payload)
            edit_message(chat_id, message_id, "اكتب نوع المصروف:")
            return
        payload.update({"التصنيف": "مصروفات", "الصنف": item, "الكمية": ""})
        set_state(user_id, name, "انتظار_إجمالي", payload)
        edit_message(chat_id, message_id, f"اكتب المبلغ الإجمالي لـ {item}:\nمثال: 250")
        return

    if data.startswith("pay:"):
        value = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        payload["طريقة الدفع"] = value
        set_state(user_id, name, "اختيار_حالة_الدفع", payload)
        edit_message(chat_id, message_id, "اختر حالة الدفع:", payment_status_menu())
        return

    if data.startswith("pstatus:"):
        value = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        payload["حالة الدفع"] = value
        operation = payload.get("العملية")
        person_type = "عميل" if operation == "بيع" else "مورد"
        if operation == "مصروف" and payload.get("الصنف") == "راتب":
            person_type = "عامل"
        set_state(user_id, name, "اختيار_طرف", payload)
        edit_message(chat_id, message_id, "اختر الطرف:", people_menu(active_people(person_type), "person"))
        return

    if data.startswith("person:"):
        person_id = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        if person_id == "new":
            set_state(user_id, name, "كتابة_طرف", payload)
            edit_message(chat_id, message_id, "اكتب اسم الطرف الجديد:")
            return
        if person_id == "none":
            payload["الطرف"] = ""
        else:
            person = find_person_by_id(person_id)
            payload["الطرف"] = person.get("الاسم", "") if person else ""
        set_state(user_id, name, "اختيار_ملاحظة", payload)
        edit_message(chat_id, message_id, "هل توجد ملاحظات؟", note_menu())
        return

    if data.startswith("note:"):
        value = data.split(":", 1)[1]
        state = get_state(user_id)
        payload = state.get("data", {})
        if value == "write":
            set_state(user_id, name, "كتابة_ملاحظة", payload)
            edit_message(chat_id, message_id, "اكتب الملاحظة:")
            return
        payload["ملاحظات"] = ""
        set_state(user_id, name, "تأكيد", payload)
        edit_message(chat_id, message_id, confirmation_text(payload), confirm_menu())
        return

    if data == "confirm":
        state = get_state(user_id)
        payload = state.get("data", {})
        operation_id = add_operation(payload, name)
        apply_inventory_effect(payload)
        clear_state(user_id, name)
        edit_message(chat_id, message_id, f"✅ تم تسجيل العملية\nرقم العملية: {operation_id}", main_menu())
        return

    edit_message(chat_id, message_id, "أمر غير معروف.", main_menu())


def handle_text(message):
    chat_id = message["chat"]["id"]
    user_id = message["from"]["id"]
    text = (message.get("text") or "").strip()
    name = user_name(user_id)

    if user_id not in ALLOWED_USERS:
        send_message(chat_id, "⛔ هذا البوت خاص")
        return

    if text in ["/start", "/menu", "/help", "القائمة"]:
        start(chat_id, user_id)
        return

    state = get_state(user_id)
    stage = state.get("stage", "")
    payload = state.get("data", {})

    if not stage:
        send_message(chat_id, "استخدم الأزرار من القائمة الرئيسية.", main_menu())
        return

    if stage == "كتابة_صنف":
        payload.update({"التصنيف": "أخرى", "الصنف": text})
        set_state(user_id, name, "انتظار_كمية", payload)
        send_message(chat_id, f"اكتب الكمية لـ {text}:")
        return

    if stage == "كتابة_مصروف":
        payload.update({"التصنيف": "مصروفات", "الصنف": text, "الكمية": ""})
        set_state(user_id, name, "انتظار_إجمالي", payload)
        send_message(chat_id, f"اكتب المبلغ الإجمالي لـ {text}:")
        return

    if stage == "انتظار_كمية":
        qty = safe_float(text)
        if qty <= 0:
            send_message(chat_id, "اكتب رقم صحيح للكمية. مثال: 5")
            return
        payload["الكمية"] = fmt_amount(qty)
        set_state(user_id, name, "انتظار_إجمالي", payload)
        send_message(chat_id, "اكتب الإجمالي بالدرهم. مثال: 250")
        return

    if stage == "انتظار_إجمالي":
        total = safe_float(text)
        if total <= 0:
            send_message(chat_id, "اكتب رقم صحيح للمبلغ. مثال: 250")
            return
        payload["الإجمالي"] = fmt_amount(total)
        set_state(user_id, name, "اختيار_دفع", payload)
        send_message(chat_id, "اختر طريقة الدفع:", payment_menu())
        return

    if stage == "كتابة_طرف":
        operation = payload.get("العملية")
        person_type = "عميل" if operation == "بيع" else "مورد"
        if operation == "مصروف" and payload.get("الصنف") == "راتب":
            person_type = "عامل"
        add_person(text, person_type)
        payload["الطرف"] = text
        set_state(user_id, name, "اختيار_ملاحظة", payload)
        send_message(chat_id, "هل توجد ملاحظات؟", note_menu())
        return

    if stage == "كتابة_ملاحظة":
        payload["ملاحظات"] = text
        set_state(user_id, name, "تأكيد", payload)
        send_message(chat_id, confirmation_text(payload), confirm_menu())
        return

    send_message(chat_id, "استخدم الأزرار لإكمال العملية أو اضغط إلغاء.", main_menu())


def confirmation_text(payload):
    return "\n".join([
        "راجع العملية:",
        f"العملية: {payload.get('العملية', '')}",
        f"التصنيف: {payload.get('التصنيف', '')}",
        f"الصنف: {payload.get('الصنف', '')}",
        f"الكمية: {payload.get('الكمية', '') or '-'}",
        f"الإجمالي: {payload.get('الإجمالي', '')} درهم",
        f"طريقة الدفع: {payload.get('طريقة الدفع', '')}",
        f"حالة الدفع: {payload.get('حالة الدفع', '')}",
        f"الطرف: {payload.get('الطرف', '') or '-'}",
        f"ملاحظات: {payload.get('ملاحظات', '') or '-'}",
    ])


def apply_inventory_effect(payload):
    item = payload.get("الصنف", "")
    qty = safe_float(payload.get("الكمية", 0))
    if not item or qty <= 0:
        return
    if payload.get("العملية") == "بيع":
        update_inventory_quantity(item, -qty)
    elif payload.get("العملية") == "شراء":
        update_inventory_quantity(item, qty)
