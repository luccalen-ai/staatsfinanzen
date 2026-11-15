"""BMF federal budget 2024-2028 (all accounts), CSV.

The BMF publishes the file as semicolon-separated with decimal commas. Its exact column set has
not been inspected from this repository yet, so the parser keeps every column, normalises names,
converts number-like columns, and fails loudly if no amount column can be found. Tighten the
mapping once the first real file has been read (see ops/TASKS.md).

Run:  python -m ingest.bmf_budget_csv
Out:  data/staging/bmf_budget_csv/budget_2024_2028.parquet
"""

from __future__ import annotations

import io
import re
import unicodedata

import pandas as pd

from ingest.common import download, staging_path

SOURCE_ID = "bmf_budget_csv"
URL = ("https://www.bmf.gv.at/dam/jcr:57d34c8f-f064-4499-8ea1-138d18fe21a9/"
       "Bundeshaushalt_Budget_2024_bis_2028.csv")

# Matches "betrag", "betrag_mio", "betrag_in_eur", "summe" ... but not "wertart" or "betragsart".
AMOUNT_COLUMN = re.compile(r"^(betrag|summe)(_|$)|_betrag$")


def normalise_name(name: str) -> str:
    name = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    name = re.sub(r"[^0-9a-zA-Z]+", "_", name).strip("_").lower()
    return name or "unnamed"


def decode(raw: bytes) -> str:
    for enc in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    raise ValueError("Could not decode BMF file")


def to_number(series: pd.Series) -> pd.Series:
    """Convert '1.234.567,89' or '-12,5' to float; leave non-numeric values as NaN."""
    s = series.astype(str).str.strip().str.replace(" ", "", regex=False)
    s = s.str.replace(".", "", regex=False).str.replace(",", ".", regex=False)
    return pd.to_numeric(s, errors="coerce")


def parse(raw: bytes | str) -> pd.DataFrame:
    text = decode(raw) if isinstance(raw, bytes) else raw
    df = pd.read_csv(io.StringIO(text), sep=";", dtype=str, keep_default_na=False)
    df.columns = [normalise_name(c) for c in df.columns]
    if len(set(df.columns)) != len(df.columns):
        raise ValueError(f"Duplicate column names after normalising: {list(df.columns)}")

    amount_cols = [c for c in df.columns if AMOUNT_COLUMN.search(c)]
    if not amount_cols:
        raise ValueError(f"No amount column found. Columns: {list(df.columns)}")

    for c in amount_cols:
        numeric = to_number(df[c])
        nonempty = df[c].str.strip() != ""
        bad = nonempty & numeric.isna()
        if bad.any():
            sample = df.loc[bad, c].head(3).tolist()
            raise ValueError(f"Column {c} has non-numeric values, e.g. {sample}")
        df[c] = numeric

    df["basis"] = "bhg"          # cash (Finanzierungshaushalt) vs accrual (Ergebnishaushalt) is split in models/
    df["source_id"] = SOURCE_ID
    return df


def main() -> None:
    raw_path = download(SOURCE_ID, URL, "Bundeshaushalt_Budget_2024_bis_2028.csv")
    df = parse(raw_path.read_bytes())
    out = staging_path(SOURCE_ID, "budget_2024_2028.parquet")
    df.to_parquet(out, index=False)
    print(f"{len(df):,} rows, columns: {list(df.columns)} -> {out}")


if __name__ == "__main__":
    main()
