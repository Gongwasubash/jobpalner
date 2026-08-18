import json
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import (
    GOOGLE_CREDENTIALS_FILE,
    GOOGLE_CREDENTIALS_JSON,
    GOOGLE_TOKEN_FILE,
    GOOGLE_TOKEN_JSON,
    SPREADSHEET_ID,
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
]


def _materialize_env_files():
    if GOOGLE_CREDENTIALS_JSON and not GOOGLE_CREDENTIALS_FILE.exists():
        GOOGLE_CREDENTIALS_FILE.write_text(GOOGLE_CREDENTIALS_JSON, encoding="utf-8")
    if GOOGLE_TOKEN_JSON and not GOOGLE_TOKEN_FILE.exists():
        GOOGLE_TOKEN_FILE.write_text(GOOGLE_TOKEN_JSON, encoding="utf-8")


def get_credentials():
    _materialize_env_files()
    creds = None
    if GOOGLE_TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(GOOGLE_TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(GOOGLE_CREDENTIALS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        GOOGLE_TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")
    return creds


def get_service():
    return build("sheets", "v4", credentials=get_credentials())


def _existing_sheet_titles(service, spreadsheet_id: str) -> set:
    meta = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
    return {s["properties"]["title"] for s in meta.get("sheets", [])}


def _sheet_title(result: dict) -> str:
    today = datetime.now().strftime("%Y-%m-%d")
    slug = result.get("title", "untitled").strip()[:40]
    forbidden = r"\/:*?[]"
    for ch in forbidden:
        slug = slug.replace(ch, "-")
    title = f"{today}-{slug}"
    return title[:100] or f"{today}-plan"


def _build_rows(result: dict, transcript: str) -> list:
    plan = result.get("plan", {})
    rows = [
        ["# " + result.get("title", "Untitled")],
        [],
        ["Branch", result.get("branch", "uncategorized")],
        ["Date", datetime.now().strftime("%Y-%m-%d")],
        ["Confidence", result.get("confidence", 0)],
        ["Tags", ", ".join(result.get("tags", []))],
        [],
        ["SUMMARY"],
        [result.get("summary", "")],
        [],
        ["OVERVIEW"],
        [plan.get("overview", "")],
        [],
        ["KEY INSIGHTS"],
    ]
    rows.extend([i] for i in plan.get("key_insights", []))
    rows.append([])
    rows.append(["ACTION STEPS"])
    for idx, s in enumerate(plan.get("action_steps", []), start=1):
        rows.append(
            [
                f"{s.get('step', idx)}. {s.get('task', '')}",
                f"Priority: {s.get('priority', '')}",
                f"Time: {s.get('estimated_time', '')}",
            ]
        )
    rows.append([])
    rows.append(["RESOURCES NEEDED"])
    rows.extend([r] for r in plan.get("resources_needed", []))
    rows.append([])
    rows.append(["POTENTIAL PROBLEMS"])
    rows.extend([p] for p in plan.get("potential_problems", []))
    rows.append([])
    rows.append(["SUCCESS METRICS"])
    rows.extend([m] for m in plan.get("success_metrics", []))
    rows.append([])
    rows.append(["ORIGINAL TRANSCRIPT"])
    rows.extend([[line] if line else [] for line in transcript.splitlines()])
    return rows


def create_plan_sheet(result: dict, transcript: str, spreadsheet_id: str = None) -> str:
    spreadsheet_id = spreadsheet_id or SPREADSHEET_ID
    service = get_service()

    sheet_title = _sheet_title(result)
    existing = _existing_sheet_titles(service, spreadsheet_id)

    n = 2
    base = sheet_title
    while sheet_title in existing:
        sheet_title = f"{base}-{n}"
        n += 1

    body = {"requests": [{"addSheet": {"properties": {"title": sheet_title}}}]}
    service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id, body=body
    ).execute()

    rows = _build_rows(result, transcript)
    service.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{sheet_title}!A1",
        valueInputOption="RAW",
        body={"values": rows},
    ).execute()
    return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit#gid=0"


def sync_if_enabled(result: dict, transcript: str) -> str | None:
    if not SPREADSHEET_ID:
        return None
    return create_plan_sheet(result, transcript)