"""Federal shareholdings report (Beteiligungsbericht 2027 und 2028, BMF), all holdings as CSV.

The BMF publishes one CSV of all holdings with a separate column description (PDF), plus a table
workbook. The column set has not been read from this repository yet, so the parser keeps every
column, normalises names and converts columns that are at least 95 % numeric.

Run:  python -m ingest.bmf_beteiligungen
Out:  data/staging/bmf_beteiligungen/beteiligungen_2027_2028.parquet
      data/extracts/bmf_beteiligungen_2027_2028.csv  (UTF-8 copy, committed for review)
"""

from __future__ import annotations

import csv
import io

import pandas as pd

from ingest.bmf_budget_csv import decode, normalise_name, to_number
from ingest.common import REPO_ROOT, download, staging_path

SOURCE_ID = "bmf_beteiligungsbericht"
BASE = "https://www.bmf.gv.at/dam/"
FILES = {
    "Beteiligungsbericht_2027_2028.csv": "jcr:80655f7f-dc57-4f1c-b4b9-11fbb14edc6d/Beteiligungsbericht_2027_2028.csv",
    "Beteiligungsbericht_2027_2028_Tabellen.xlsx": "jcr:82231825-7698-42e1-9a15-2a9d558d1339/Beteiligungsbericht_2027_2028_Tabellen.xlsx",
    "Spaltenbeschreibung_2027_2028.pdf": "jcr:e2c103dd-d7ce-4853-8fb8-589ac853aca7/Spaltenbeschreibung_Beteilligungen_CSV_2027_2028.pdf",
}


def parse(raw: bytes | str) -> pd.DataFrame:
    text = decode(raw) if isinstance(raw, bytes) else raw
    sep = csv.Sniffer().sniff(text[:20000], delimiters=";,\t").delimiter
    df = pd.read_csv(io.StringIO(text), sep=sep, dtype=str, keep_default_na=False)
    df.columns = [normalise_name(c) for c in df.columns]
    seen: dict[str, int] = {}
    cols = []
    for c in df.columns:            # make duplicates unique instead of failing: this file is wide
        seen[c] = seen.get(c, 0) + 1
        cols.append(c if seen[c] == 1 else f"{c}_{seen[c]}")
    df.columns = cols
    for c in df.columns:
        s = df[c].str.strip()
        nonempty = s != ""
        if nonempty.sum() == 0:
            continue
        num = to_number(s)
        if num[nonempty].notna().mean() >= 0.95 and not s[nonempty].str.match(r"^0\d").any():
            df[c] = num
    df["source_id"] = SOURCE_ID
    return df


def main() -> None:
    paths = {name: download(SOURCE_ID, BASE + path, name) for name, path in FILES.items()}
    raw = paths["Beteiligungsbericht_2027_2028.csv"].read_bytes()
    df = parse(raw)
    out = staging_path(SOURCE_ID, "beteiligungen_2027_2028.parquet")
    df.to_parquet(out, index=False)
    extract = REPO_ROOT / "data" / "extracts" / "bmf_beteiligungen_2027_2028.csv"
    extract.parent.mkdir(parents=True, exist_ok=True)
    extract.write_text(decode(raw), encoding="utf-8")
    # The column description is a PDF: keep its text next to the extract so it can be read here.
    try:
        import pdfplumber
        with pdfplumber.open(paths["Spaltenbeschreibung_2027_2028.pdf"]) as pdf:
            txt = "\n".join(page.extract_text() or "" for page in pdf.pages)
        (extract.parent / "bmf_beteiligungen_spaltenbeschreibung.txt").write_text(txt, encoding="utf-8")
    except Exception as e:  # noqa: BLE001 - the description is a help, not a requirement
        print(f"Column description not extracted: {e}")
    print(f"{len(df):,} rows, columns: {list(df.columns)} -> {out}")


if __name__ == "__main__":
    main()
