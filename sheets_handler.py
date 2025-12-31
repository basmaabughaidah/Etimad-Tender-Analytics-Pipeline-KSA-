%%bash
cat > /content/drive/MyDrive/opportunity_agent/sheets_handler.py << 'PY'
# -*- coding: utf-8 -*-
import os, json, pickle
from googleapiclient.discovery import build
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials as SA_Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from config import SHEET_ID, SHEET_TAB, SHEET_COLUMNS

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _load_credentials():
    cred_path = "credentials.json"
    if not os.path.exists(cred_path):
        raise FileNotFoundError("credentials.json غير موجود في المسار الحالي.")

    with open(cred_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Service Account
    if isinstance(data, dict) and data.get("type") == "service_account" and data.get("client_email"):
        return SA_Credentials.from_service_account_file(cred_path, scopes=SCOPES)

    # OAuth Client (Console Flow)
    creds = None
    token_path = "token.json"
    if os.path.exists(token_path):
        with open(token_path, "rb") as t:
            creds = pickle.load(t)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            # لا نحاول فتح متصفح في كولاب
            creds = flow.run_console()
        with open(token_path, "wb") as t:
            pickle.dump(creds, t)
    return creds

def _svc():
    creds = _load_credentials()
    return build("sheets", "v4", credentials=creds).spreadsheets()

def _ensure_headers():
    s = _svc()
    res = s.values().get(spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1:Z1").execute()
    cur = res.get("values", [])
    if not cur or cur[0] != SHEET_COLUMNS:
        s.values().update(
            spreadsheetId=SHEET_ID,
            range=f"{SHEET_TAB}!A1",
            valueInputOption="RAW",
            body={"values": [SHEET_COLUMNS]},
        ).execute()

def _read_existing_refs():
    s = _svc()
    res = s.values().get(spreadsheetId=SHEET_ID, range=f"{SHEET_TAB}!A1:Z1000000").execute()
    vals = res.get("values", [])
    if not vals:
        return set()
    hdr, rows = vals[0], vals[1:]
    if "الرقم المرجعي" not in hdr:
        return set()
    i = hdr.index("الرقم المرجعي")
    return set(r[i] for r in rows if len(r) > i and r[i])

def _append_rows(items):
    if not items:
        return
    s = _svc()
    rows = [[(itm.get(c) or "").strip() for c in SHEET_COLUMNS] for itm in items]
    s.values().append(
        spreadsheetId=SHEET_ID,
        range=f"{SHEET_TAB}!A1",
        valueInputOption="RAW",
        insertDataOption="INSERT_ROWS",
        body={"values": rows},
    ).execute()

def update_sheet(items):
    _ensure_headers()
    existing = _read_existing_refs()
    new_items = []
    for it in items:
        ref = (it.get("الرقم المرجعي") or "").strip()
        if ref and ref in existing:
            continue
        new_items.append(it)
    _append_rows(new_items)
PY
