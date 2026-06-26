# app/config.py

import os

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
GOOGLE_SERVICE_ACCOUNT_JSON = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "")
SPREADSHEET_ID = os.environ.get("SPREADSHEET_ID", "")

ALLOWED_USERS = {
    47329648: "Khaled",
    6894180427: "Hamad",
}

SHEET_OPERATIONS = "العمليات"
SHEET_INVENTORY = "الجرد"
SHEET_PEOPLE = "الأشخاص"
SHEET_STATE = "الحالة"
