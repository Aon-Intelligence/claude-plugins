"""Site backup and restore for Azure Blob Storage static websites."""

import re
from datetime import datetime, timezone
from typing import Any, Dict, List

from blob_container_client import (
    BACKUP_PREFIX,
    copy_blob_in_container,
    delete_blob,
    list_blob_names,
)

BACKUP_ID_PATTERN = re.compile(r"^\d{11}$")  # YYYYMMDD + 3-digit sequence


def _is_backup_path(blob_name: str) -> bool:
    return blob_name == BACKUP_PREFIX.rstrip("/") or blob_name.startswith(BACKUP_PREFIX)


def _backup_id_from_blob_name(blob_name: str) -> str | None:
    if not blob_name.startswith(BACKUP_PREFIX):
        return None
    remainder = blob_name[len(BACKUP_PREFIX) :]
    backup_id = remainder.split("/", 1)[0]
    if BACKUP_ID_PATTERN.match(backup_id):
        return backup_id
    return None


def _site_blob_names() -> List[str]:
    return [name for name in list_blob_names() if not _is_backup_path(name)]


def _next_backup_id(existing_ids: List[str]) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    max_seq = 0
    for backup_id in existing_ids:
        if backup_id.startswith(today):
            max_seq = max(max_seq, int(backup_id[8:]))
    return f"{today}{max_seq + 1:03d}"


def create_site_backup() -> Dict[str, Any]:
    """Copy all live site blobs into backups/YYYYMMDD###/."""
    existing = list_site_backups()
    backup_id = _next_backup_id([entry["id"] for entry in existing])
    prefix = f"{BACKUP_PREFIX}{backup_id}/"

    copied: List[str] = []
    for blob_name in _site_blob_names():
        copy_blob_in_container(blob_name, f"{prefix}{blob_name}")
        copied.append(blob_name)

    return {
        "backup_id": backup_id,
        "files_copied": len(copied),
        "files": copied,
    }


def list_site_backups() -> List[Dict[str, Any]]:
    """List backup versions under backups/ with file counts."""
    backups: Dict[str, Dict[str, Any]] = {}

    for blob_name in list_blob_names(prefix=BACKUP_PREFIX):
        backup_id = _backup_id_from_blob_name(blob_name)
        if backup_id is None:
            continue

        relative_path = blob_name[len(f"{BACKUP_PREFIX}{backup_id}/") :]
        if not relative_path:
            continue

        entry = backups.setdefault(
            backup_id,
            {"id": backup_id, "file_count": 0, "files": []},
        )
        entry["file_count"] += 1
        entry["files"].append(relative_path)

    return sorted(backups.values(), key=lambda item: item["id"], reverse=True)


def _backup_blob_names(backup_id: str) -> List[str]:
    if not BACKUP_ID_PATTERN.match(backup_id):
        raise ValueError(
            f"Invalid backup_id '{backup_id}'. Expected format YYYYMMDD### "
            "(e.g. 20260710001)."
        )

    prefix = f"{BACKUP_PREFIX}{backup_id}/"
    names = list_blob_names(prefix=prefix)
    if not names:
        raise ValueError(f"Backup '{backup_id}' was not found.")

    return names


def restore_site_backup(backup_id: str) -> Dict[str, Any]:
    """Replace the live site with a backup version (backups/ is never touched)."""
    backup_blobs = _backup_blob_names(backup_id)
    prefix = f"{BACKUP_PREFIX}{backup_id}/"

    deleted: List[str] = []
    for blob_name in _site_blob_names():
        delete_blob(blob_name)
        deleted.append(blob_name)

    restored: List[str] = []
    for blob_name in backup_blobs:
        relative_path = blob_name[len(prefix) :]
        copy_blob_in_container(blob_name, relative_path)
        restored.append(relative_path)

    return {
        "backup_id": backup_id,
        "files_deleted": len(deleted),
        "files_restored": len(restored),
        "files": restored,
    }
