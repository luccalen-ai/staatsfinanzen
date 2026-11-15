"""Vienna budget (Voranschlag) and accounts (Rechnungsabschluss) under VRV 2015, from data.gv.at.

Vienna is both a Land and a Gemeinde. The files are found through the data.gv.at catalogue
(CKAN API) rather than hard-coded links, and the discovery result is saved so a human can see
exactly which datasets were used.

The column layout of these CSVs has not yet been inspected from this repository. The parser keeps
every column, keeps code columns (Ansatz, Konto, MVAG, ...) as text so leading zeros survive, and
treats a column as an amount only if almost all its values are numbers. Tighten the mapping after
the first real run (see ops/ingest_report.md).

Run:  python -m ingest.wien_haushalt [--years 2020-2026]
Out:  data/staging/wien_haushalt/discovery.json and one parquet per file
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re

import pandas as pd
import requests

from ingest.bmf_budget_csv import decode, normalise_name, to_number
from ingest.common import USER_AGENT, download, staging_path

SOURCE_ID = "wien_ogd_haushalt"
QUERIES = ["Rechnungsabschluss Wien", "Voranschlag Wien"]

# Columns that hold codes or labels, never amounts, even if they look numeric.
CODE_COLUMN = re.compile(
    r"(ansatz|konto|mvag|gkz|gemeinde|jahr|year|haushalt|code|nr|kennz|sektor|bezeichnung|text|uab|ugl)"
)


def _ckan(endpoint: str, q: str) -> list[dict]:
    r = requests.get(endpoint, params={"q": q, "rows": 200}, headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()
    out = []
    for pkg in r.json()["result"]["results"]:
        for res in pkg.get("resources", []):
            out.append({
                "dataset_title": pkg.get("title", ""),
                "dataset_id": pkg.get("id"),
                "licence": pkg.get("license_title") or pkg.get("license_id"),
                "organization": (pkg.get("organization") or {}).get("title"),
                "format": (res.get("format") or ""),
                "resource_name": res.get("name"),
                "url": res.get("url"),
            })
    return out


def _text(v) -> str:
    """piveau returns multilingual fields as {"de": "...", "en": "..."}."""
    if isinstance(v, dict):
        return v.get("de") or v.get("en") or next(iter(v.values()), "")
    return v or ""


def _piveau(endpoint: str, q: str) -> list[dict]:
    params = {"q": q, "filter": "dataset", "limit": 200, "facets": json.dumps({"country": ["at"]})}
    r = requests.get(endpoint, params=params, headers={"User-Agent": USER_AGENT}, timeout=60)
    r.raise_for_status()
    out = []
    for ds in r.json()["result"]["results"]:
        for dist in ds.get("distributions", []):
            urls = dist.get("download_url") or dist.get("access_url") or []
            url = urls[0] if isinstance(urls, list) and urls else urls
            fmt = dist.get("format") or {}
            out.append({
                "dataset_title": _text(ds.get("title")),
                "dataset_id": ds.get("id"),
                "licence": _text((dist.get("license") or {}).get("label")) if isinstance(dist.get("license"), dict) else dist.get("license"),
                "organization": _text((ds.get("publisher") or {}).get("name")),
                "format": (fmt.get("id") or fmt.get("label") or "") if isinstance(fmt, dict) else str(fmt),
                "resource_name": _text(dist.get("title")),
                "url": url,
            })
    return out


# Tried in order; every attempt is logged so the report shows which catalogue answered.
ENDPOINTS = [
    ("ckan", "https://www.data.gv.at/katalog/api/3/action/package_search"),
    ("ckan", "https://www.data.gv.at/api/3/action/package_search"),
    ("piveau", "https://www.data.gv.at/api/hub/search/search"),
    ("piveau", "https://data.europa.eu/api/hub/search/search"),
]


def discover(years: range, log: list[dict]) -> list[dict]:
    """Find CSV files of Vienna's VA or RA for the given years. Appends one entry per attempt to log."""
    candidates: list[dict] = []
    for kind, endpoint in ENDPOINTS:
        try:
            for q in QUERIES:
                candidates += (_ckan if kind == "ckan" else _piveau)(endpoint, q)
            log.append({"endpoint": endpoint, "ok": True, "items": len(candidates)})
            if candidates:
                break
        except Exception as exc:  # noqa: BLE001 - try the next catalogue
            log.append({"endpoint": endpoint, "ok": False, "error": f"{type(exc).__name__}: {exc}"[:300]})
    return select(candidates, years)


def select(candidates: list[dict], years: range) -> list[dict]:
    found: dict[str, dict] = {}
    for c in candidates:
        title, url = c["dataset_title"], c.get("url")
        if not url or "csv" not in (c.get("format") or "").lower():
            continue
        if not re.search(r"\bWien\b", title):
            continue
        year_match = re.search(r"(20\d\d)", title)
        if not year_match or int(year_match.group(1)) not in years:
            continue
        kind = ("rechnungsabschluss" if "Rechnungsabschluss" in title
                else "voranschlag" if "Voranschlag" in title else None)
        if kind is None:
            continue
        found[url] = {**c, "kind": kind, "year": int(year_match.group(1))}
    return sorted(found.values(), key=lambda d: (d["kind"], d["year"], d["url"]))


def parse(raw: bytes | str) -> pd.DataFrame:
    text = decode(raw) if isinstance(raw, bytes) else raw
    sep = ";" if text.split("\n", 1)[0].count(";") >= text.split("\n", 1)[0].count(",") else ","
    df = pd.read_csv(io.StringIO(text), sep=sep, dtype=str, keep_default_na=False)
    df.columns = [normalise_name(c) for c in df.columns]

    amount_cols = []
    for c in df.columns:
        if CODE_COLUMN.search(c):
            continue
        values = df[c].str.strip()
        nonempty = values != ""
        if nonempty.sum() == 0:
            continue
        numeric = to_number(values[nonempty])
        if numeric.notna().mean() >= 0.95:
            amount_cols.append(c)
            df[c] = to_number(values)
    if not amount_cols:
        raise ValueError(f"No amount column recognised. Columns: {list(df.columns)}")
    df.attrs["amount_columns"] = amount_cols
    return df


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--years", default="2020-2026")
    args = ap.parse_args()
    first, last = (int(x) for x in args.years.split("-"))

    log: list[dict] = []
    resources = discover(range(first, last + 1), log)
    staging_path(SOURCE_ID, "discovery_log.json").write_text(json.dumps(log, indent=2, ensure_ascii=False))
    staging_path(SOURCE_ID, "discovery.json").write_text(
        json.dumps(resources, indent=2, ensure_ascii=False))
    print(f"{len(resources)} CSV resources found")

    for res in resources:
        url_tag = hashlib.sha256(res["url"].encode()).hexdigest()[:8]  # stable across runs
        name = f"{res['kind']}_{res['year']}_{url_tag}.csv"
        try:
            raw_path = download(SOURCE_ID, res["url"], name)
            df = parse(raw_path.read_bytes())
        except Exception as exc:  # noqa: BLE001 - one bad file must not stop the others
            print(f"FAILED {res['url']}: {exc}")
            continue
        df["kind"], df["year"], df["source_url"] = res["kind"], res["year"], res["url"]
        df.to_parquet(staging_path(SOURCE_ID, name.replace(".csv", ".parquet")), index=False)
        print(f"{name}: {len(df):,} rows, amounts in {df.attrs['amount_columns']}")


if __name__ == "__main__":
    main()
