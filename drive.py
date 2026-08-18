from pathlib import Path

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from sheets import get_credentials

DRIVE_ROOT = "IdeaExecuter"


def _ensure_folder(service, name: str, parent: str = None) -> str:
    q = f"name='{name}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    if parent:
        q += f" and '{parent}' in parents"
    resp = service.files().list(q=q, fields="files(id, name)", spaces="drive").execute()
    files = resp.get("files", [])
    if files:
        return files[0]["id"]

    body = {"name": name, "mimeType": "application/vnd.google-apps.folder"}
    if parent:
        body["parents"] = [parent]
    f = service.files().create(body=body, fields="id").execute()
    return f["id"]


def upload_plan_md(md_path: str, branch: str) -> str:
    service = build("drive", "v3", credentials=get_credentials())

    root_id = _ensure_folder(service, DRIVE_ROOT)
    branch_id = _ensure_folder(service, branch, root_id)

    fname = Path(md_path).name
    media = MediaFileUpload(md_path, mimetype="text/markdown")
    f = service.files().create(
        body={"name": fname, "parents": [branch_id]},
        media_body=media,
        fields="id, webViewLink",
    ).execute()
    return f.get("webViewLink", f"https://drive.google.com/file/d/{f['id']}/view")