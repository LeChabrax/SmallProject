"""Google Drive helpers — upload + share + sheet integration.

Used by `generate_contract.py --upload-drive --update-sheet` to push a
freshly generated PDF contract into the `InfluenceContract` Drive folder
and write the resulting link in the right column of the Google Sheet.

This module uses `google-api-python-client` directly (NOT gspread), so the
same dependency family covers both Drive and Sheets calls. Install via:

    pip install google-api-python-client google-auth

The service account at `~/.config/google-service-account.json` already has
write access to the `InfluenceContract` folder (verified 2026-04-13).
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

# Drive folder containing all signed and draft contracts.
INFLUENCE_CONTRACT_FOLDER_ID = "1dxT2gSAm6tcnd8Ck6hXxPDS5yieMuj4x"

DEFAULT_CREDS_PATH = Path.home() / ".config" / "google-service-account.json"

DRIVE_SCOPES = [
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/spreadsheets",
]


@lru_cache(maxsize=1)
def _credentials():
    from google.oauth2 import service_account

    path = os.getenv("GOOGLE_SERVICE_ACCOUNT_PATH", str(DEFAULT_CREDS_PATH))
    return service_account.Credentials.from_service_account_file(
        path, scopes=DRIVE_SCOPES
    )


@lru_cache(maxsize=1)
def drive_service():
    from googleapiclient.discovery import build

    return build("drive", "v3", credentials=_credentials(), cache_discovery=False)


@lru_cache(maxsize=1)
def sheets_service():
    from googleapiclient.discovery import build

    return build("sheets", "v4", credentials=_credentials(), cache_discovery=False)


def upload_pdf_to_drive(
    local_path: str,
    drive_filename: Optional[str] = None,
    folder_id: str = INFLUENCE_CONTRACT_FOLDER_ID,
    overwrite_existing: bool = True,
) -> Dict[str, Any]:
    """Upload a local PDF into the Drive folder and return its metadata.

    Args:
        local_path: filesystem path to the PDF.
        drive_filename: name of the file as stored on Drive. If None, uses
            `os.path.basename(local_path)`.
        folder_id: parent Drive folder id. Defaults to the Impulse
            `InfluenceContract` folder.
        overwrite_existing: if a file with the same name already exists in the
            folder, replace it (keep the same Drive id, updates content). If
            False, a new file is created with a duplicate name.

    Returns:
        ``{"id": ..., "name": ..., "webViewLink": ..., "webContentLink": ...}``
    """
    from googleapiclient.http import MediaFileUpload

    if not os.path.exists(local_path):
        raise FileNotFoundError(local_path)

    name = drive_filename or os.path.basename(local_path)
    svc = drive_service()
    media = MediaFileUpload(local_path, mimetype="application/pdf", resumable=False)

    if overwrite_existing:
        # Look up existing file with same name in this folder.
        q = (
            f"'{folder_id}' in parents and name = '{name}' "
            f"and trashed = false and mimeType = 'application/pdf'"
        )
        existing = (
            svc.files()
            .list(
                q=q,
                fields="files(id,name,webViewLink)",
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
                pageSize=1,
            )
            .execute()
            .get("files", [])
        )
        if existing:
            file_id = existing[0]["id"]
            updated = (
                svc.files()
                .update(
                    fileId=file_id,
                    media_body=media,
                    fields="id,name,webViewLink,webContentLink",
                    supportsAllDrives=True,
                )
                .execute()
            )
            return updated

    # Create new file
    metadata = {"name": name, "parents": [folder_id], "mimeType": "application/pdf"}
    created = (
        svc.files()
        .create(
            body=metadata,
            media_body=media,
            fields="id,name,webViewLink,webContentLink",
            supportsAllDrives=True,
        )
        .execute()
    )
    return created


def find_row_by_name(
    spreadsheet_id: str,
    tab: str,
    prenom_col_letter: str,
    nom_col_letter: str,
    target_first_name: str,
    target_last_name: str,
    header_rows: int = 3,
    max_rows: int = 1000,
) -> Optional[int]:
    """Return the 1-indexed row number of an ambassador in a Sheet tab.

    Matches case-insensitively on first_name + last_name. Returns None if no
    match is found. Used by `generate_contract.py --update-sheet`.
    """
    svc = sheets_service()
    rng = f"{tab}!{prenom_col_letter}{header_rows + 1}:{nom_col_letter}{max_rows}"
    res = (
        svc.spreadsheets()
        .values()
        .get(spreadsheetId=spreadsheet_id, range=rng)
        .execute()
    )
    rows = res.get("values", [])

    target = (
        target_first_name.strip().lower(),
        target_last_name.strip().lower(),
    )

    # Determine which column index is which (the order in the range matches
    # ascending letter order, i.e. lower letter first).
    prenom_first = prenom_col_letter < nom_col_letter
    for i, row in enumerate(rows):
        if not row:
            continue
        if prenom_first:
            prenom = (row[0] if len(row) > 0 else "").strip().lower()
            nom = (
                row[ord(nom_col_letter) - ord(prenom_col_letter)].strip().lower()
                if len(row) > (ord(nom_col_letter) - ord(prenom_col_letter))
                else ""
            )
        else:
            nom = (row[0] if len(row) > 0 else "").strip().lower()
            prenom = (
                row[ord(prenom_col_letter) - ord(nom_col_letter)].strip().lower()
                if len(row) > (ord(prenom_col_letter) - ord(nom_col_letter))
                else ""
            )
        if (prenom, nom) == target:
            return header_rows + 1 + i
    return None


def write_cell(
    spreadsheet_id: str,
    tab: str,
    cell_a1: str,
    value: str,
) -> None:
    """Write a single cell value via the Sheets API."""
    svc = sheets_service()
    svc.spreadsheets().values().update(
        spreadsheetId=spreadsheet_id,
        range=f"{tab}!{cell_a1}",
        valueInputOption="USER_ENTERED",
        body={"values": [[value]]},
    ).execute()


# ---------------------------------------------------------------------------
# Sheet routing — où écrire le lien Drive selon le type de contrat
# ---------------------------------------------------------------------------

# Mapping (contract_type → tab, prenom_col, nom_col, link_col).
# Updated 2026-04-13 against `knowledge/reference/sheet_schema.md`.
SHEET_CONTRACT_ROUTING = {
    # No "ambassadeur" type yet in generate_contract.py — kept for future use.
    "ambassadeur": ("Suivi_Amb", "AE", "AD", "AK"),
    "dotation":    ("Suivi_Dot", "H",  "I",  "AE"),
    "paid":        ("Suivi_Paid", "G",  "H",  "AM"),
}

SHEET_ID = "1cKuWT2yhtVgg7RGrkHJW0pOF9bENoK2xU0SQ81u06y4"


def update_sheet_with_contract_link(
    contract_type: str,
    first_name: str,
    last_name: str,
    drive_link: str,
    spreadsheet_id: str = SHEET_ID,
) -> Tuple[Optional[int], Optional[str]]:
    """Write `drive_link` into the right Sheet column based on contract type.

    Returns ``(row_number, cell_a1)`` if the row was found, or
    ``(None, None)`` if the ambassador is not yet in the sheet.
    """
    if contract_type not in SHEET_CONTRACT_ROUTING:
        raise ValueError(f"unknown contract_type: {contract_type!r}")
    tab, prenom_col, nom_col, link_col = SHEET_CONTRACT_ROUTING[contract_type]
    row = find_row_by_name(
        spreadsheet_id, tab, prenom_col, nom_col, first_name, last_name
    )
    if row is None:
        return (None, None)
    cell = f"{link_col}{row}"
    write_cell(spreadsheet_id, tab, cell, drive_link)
    return (row, cell)
