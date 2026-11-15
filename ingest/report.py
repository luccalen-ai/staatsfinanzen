"""Write ops/ingest_report.md: what each ingest run produced, so it can be reviewed without the data.

Run after the ingest scripts:  python -m ingest.report
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

import pandas as pd
import yaml

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


def control_checks() -> list[str]:
    """Compare parsed data with published totals from ops/control_totals.yaml."""
    spec = yaml.safe_load((REPO_ROOT / "ops" / "control_totals.yaml").read_text())["controls"]
    lines = ["## Control totals", "", "| Check | Expected | Parsed | Difference | Result |", "| --- | --- | --- | --- | --- |"]
    for c in spec:
        paths = sorted(STAGING_DIR.glob(c["table"]))
        if not paths:
            lines.append(f"| {c['id']} | {c['expected']:,.1f} | no table | | skipped |")
            continue
        if not c.get("column"):
            lines.append(f"| {c['id']} | {c['expected']:,.1f} | column not mapped yet | | skipped |")
            continue
        df = pd.concat(pd.read_parquet(p) for p in paths)
        for k, v in c["filter"].items():
            df = df[df[k].astype(str) == str(v)]
        if df.empty:
            lines.append(f"| {c['id']} | {c['expected']:,.1f} | no matching rows | | skipped |")
            continue
        parsed = float(df[c["column"]].sum()) * c["multiplier"]
        diff = (parsed - c["expected"]) / c["expected"]
        result = "pass" if abs(diff) <= c["tolerance"] else "FAIL"
        lines.append(f"| {c['id']} | {c['expected']:,.1f} | {parsed:,.1f} | {diff:+.2%} | {result} |")
    return lines + [""]


def main() -> None:
    lines = [f"# Ingest report", "", f"Generated {dt.datetime.utcnow():%Y-%m-%d %H:%M} UTC by the `ingest` workflow.", ""]

    lines += ["## Downloaded files", "", "| File | Bytes | SHA-256 | URL |", "| --- | --- | --- | --- |"]
    for manifest in sorted(RAW_DIR.glob("*/*/manifest.json")):
        for entry in json.loads(manifest.read_text()).values():
            lines.append(f"| {entry['doc_id']} | {entry['bytes']:,} | `{entry['sha256'][:12]}` | {entry['url']} |")
    lines.append("")

    log_path = STAGING_DIR / "wien_ogd_haushalt" / "discovery_log.json"
    if log_path.exists():
        lines += ["## Vienna catalogue attempts", "", "| Endpoint | OK | Items or error |", "| --- | --- | --- |"]
        for a in json.loads(log_path.read_text()):
            lines.append(f"| {a['endpoint']} | {a['ok']} | {a.get('items', a.get('error', ''))} |".replace("\n", " "))
        heads = [a for a in json.loads(log_path.read_text()) if a.get("head")]
        if heads:
            lines += ["", "First bytes returned by the first failed download:", "", "```", heads[0]["head"], "```"]
        lines.append("")

    lines += control_checks()

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
