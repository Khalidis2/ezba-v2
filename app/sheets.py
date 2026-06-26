# app/sheets.py

import json
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from app.config import GOOGLE_SERVICE_ACCOUNT_JSON, SPREADSHEET_ID


SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


def service():
    info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
    creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    return build("sheets", "v4", credentials=creds)


def read_rows(sheet_name, range_name="A1:Z"):
    svc = service()
    result = svc.spreadsheets().values().get(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!{range_name}",
    ).execute()
    return result.get("values", [])


def append_row(sheet_name, row):
    svc = service()
    svc.spreadsheets().values().append(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A1",
        valueInputOption="USER_ENTERED",
        body={"values": [row]},
    ).execute()


def update_row(sheet_name, row_number, values):
    svc = service()
    end_col = chr(ord("A") + len(values) - 1)
    svc.spreadsheets().values().update(
        spreadsheetId=SPREADSHEET_ID,
        range=f"{sheet_name}!A{row_number}:{end_col}{row_number}",
        valueInputOption="USER_ENTERED",
        body={"values": [values]},
    ).execute()


def rows_to_dicts(rows):
    if not rows:
        return []
    headers = rows[0]
    output = []
    for index, row in enumerate(rows[1:], start=2):
        if not any(row):
            continue
        record = {"_row": index}
        for i, header in enumerate(headers):
            record[header] = row[i] if i < len(row) else ""
        output.append(record)
    return output


def get_records(sheet_name):
    return rows_to_dicts(read_rows(sheet_name))
