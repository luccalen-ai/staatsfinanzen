"""Write ops/ingest_report.md: what each ingest run produced, so it can be reviewed without the data.

Run after the ingest scripts:  python -m ingest.report
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pandas as pd

from ingest.common import RAW_DIR, REPO_ROOT, STAGING_DIR

OUT = REPO_ROOT / "ops" / "ingest_report.md"


def describe(path: Path) -> list[str]:
    df = pd.read_parquet(path)
    lines = [f"### `{path.relative_to(STAGING_DIR)}`", "",
             f"{len(df):,} rows, {len(df.columns)} columns.", "",
             "| Column | Type | Non-empty | Example values |", "| --- | --- | --- | --- |"]
    for c in df.columns:
        s = df[c]
        examples = ", ".join(str(v) for v in s.dropna().astype(str).unique()[:4]).replace("|", "/")
        lines.append(f"| {c} | {s.dtype} | {int(s.notna().sum()):,} | {examples[:120]} |")
    num = df.select_dtypes("number")
    if not num.empty:
        lines += ["", "Numeric sums: " + ", ".join(f"{c} = {num[c].sum():,.2f}" for c in num.columns)]
    return lines + [""]


def main() -> None:
    lines = [f"# Ingest report", "", f"Generated {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC by the `ingest` workflow.", ""]

    lines += ["## Downloaded files", "", "| File | Bytes | SHA-256 | URL |", "| --- | --- | --- | --- |"]
    for manifest in sorted(RAW_DIR.glob("*/*/manifest.json")):
        for entry in json.loads(manifest.read_text()).values():
            lines.append(f"| {entry['doc_id']} | {entry['bytes']:,} | `{entry['sha256'][:12]}` | {entry['url']} |")
    lines.append("")

    discovery = STAGING_DIR / "wien_ogd_haushalt" / "discovery.json"
    if discovery.exists():
        lines += ["## Vienna datasets found on data.gv.at", "",
                  "| Kind | Year | Dataset | Licence | Organisation |", "| --- | --- | --- | --- | --- |"]
        for r in json.loads(discovery.read_text()):
            lines.append(f"| {r['kind']} | {r['year']} | {r['dataset_title']} | {r['licence']} | {r['organization']} |")
        lines.append("")

    lines += ["## Staging tables", ""]
    for p in sorted(STAGING_DIR.glob("*/*.parquet")):
        try:
            lines += describe(p)
        except Exception as exc:  # noqa: BLE001
            lines += [f"### `{p.name}`", "", f"Could not read: {exc}", ""]

    OUT.write_text("\n".join(lines))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
