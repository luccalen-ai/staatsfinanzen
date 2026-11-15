"""Shared helpers for ingest scripts: download, raw storage with hashes, manifest."""

from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

import requests

REPO_ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = REPO_ROOT / "data" / "raw"
STAGING_DIR = REPO_ROOT / "data" / "staging"

USER_AGENT = "staatsfinanzen-ingest/0.1 (+https://github.com/luccalen-ai/staatsfinanzen)"


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(source_id: str, url: str, filename: str, retrieved: dt.date | None = None) -> Path:
    """Download url into data/raw/<source_id>/<date>/<filename> and record it in the manifest.

    The raw file is never modified afterwards. Re-running on the same day reuses the file.
    """
    retrieved = retrieved or dt.date.today()
    target_dir = RAW_DIR / source_id / retrieved.isoformat()
    target_dir.mkdir(parents=True, exist_ok=True)
    target = target_dir / filename
    if not target.exists():
        with requests.get(url, headers={"User-Agent": USER_AGENT}, stream=True, timeout=300) as r:
            r.raise_for_status()
            tmp = target.with_suffix(target.suffix + ".part")
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1 << 20):
                    f.write(chunk)
            tmp.rename(target)
    record_in_manifest(source_id, url, target, retrieved)
    return target


def record_in_manifest(source_id: str, url: str, path: Path, retrieved: dt.date) -> dict:
    manifest_path = path.parent / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {}
    entry = {
        "doc_id": f"{source_id}/{retrieved.isoformat()}/{path.name}",
        "source_id": source_id,
        "url": url,
        "retrieved_at": retrieved.isoformat(),
        "sha256": sha256_of(path),
        "bytes": path.stat().st_size,
    }
    manifest[path.name] = entry
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))
    return entry


def staging_path(source_id: str, name: str) -> Path:
    d = STAGING_DIR / source_id
    d.mkdir(parents=True, exist_ok=True)
    return d / name
