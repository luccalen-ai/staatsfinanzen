"""Eurostat gov_10a_exp: general government expenditure by function (COFOG).

Downloads Austria plus peer countries for all subsectors, COFOG levels I and II, and the
transactions we use, then writes a tidy staging table.

Run:  python -m ingest.eurostat_cofog [--start 2015]
Out:  data/staging/eurostat_cofog/gov_10a_exp.parquet
"""

from __future__ import annotations

import argparse
import io

import pandas as pd

from ingest.common import download, staging_path

SOURCE_ID = "eurostat_cofog"
BASE = "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/gov_10a_exp"

# EU peers proposed in ops/DECISIONS.md (not yet confirmed); Switzerland is not in this dataset for all years.
GEO = ["AT", "DE", "NL", "DK", "SE", "EU27_2020"]
SECTORS = ["S13", "S1311", "S1312", "S1313", "S1314"]
UNITS = ["MIO_EUR", "PC_GDP"]
NA_ITEMS = ["TE", "D1", "P2", "D62_D632", "D3", "D7", "P5", "D9"]  # total, staff, inputs, social benefits, subsidies, current & capital transfers, investment

# Maps Eurostat sector codes to our gov_unit ids (Vienna is split later from national sources).
SECTOR_TO_UNIT = {
    "S13": "at_general_government",
    "S1311": "bund",
    "S1312": "laender",
    "S1313": "gemeinden",
    "S1314": "social_security",
}


def build_url(start: int) -> str:
    key = ".".join(["A", "+".join(UNITS), "+".join(SECTORS), "", "+".join(NA_ITEMS), "+".join(GEO)])
    # Empty cofog99 position = all COFOG codes
    return f"{BASE}/{key}?format=SDMX-CSV&startPeriod={start}"


def parse(raw: bytes | str) -> pd.DataFrame:
    """Parse Eurostat SDMX-CSV into a tidy frame. Pure function, tested offline."""
    text = raw.decode("utf-8") if isinstance(raw, bytes) else raw
    df = pd.read_csv(io.StringIO(text), dtype=str)
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    required = {"freq", "unit", "sector", "cofog99", "na_item", "geo", "time_period", "obs_value"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Eurostat file is missing columns: {sorted(missing)}")

    df = df[df["obs_value"].notna() & (df["obs_value"].str.strip() != "")].copy()
    df["year"] = df["time_period"].str[:4].astype(int)
    df["value"] = pd.to_numeric(df["obs_value"], errors="raise")
    df["flag"] = df.get("obs_flag")

    # Amounts in million EUR become EUR; % of GDP stays a ratio column.
    df["amount_eur"] = df["value"].where(df["unit"] == "MIO_EUR") * 1_000_000
    df["pct_gdp"] = df["value"].where(df["unit"] == "PC_GDP")

    df["cofog_code"] = df["cofog99"]
    df["cofog_depth"] = df["cofog_code"].map(lambda c: 0 if c == "TOTAL" else (1 if len(c) == 4 else 2))
    df["unit_id"] = df["sector"].map(SECTOR_TO_UNIT).where(df["geo"] == "AT")
    df["basis"] = "esa2010"
    df["consolidated"] = True

    cols = ["geo", "year", "sector", "unit_id", "cofog_code", "cofog_depth", "na_item",
            "unit", "value", "amount_eur", "pct_gdp", "flag", "basis", "consolidated"]
    return df[cols].sort_values(["geo", "sector", "cofog_code", "na_item", "unit", "year"]).reset_index(drop=True)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=2015)
    args = ap.parse_args()

    raw_path = download(SOURCE_ID, build_url(args.start), "gov_10a_exp.csv")
    df = parse(raw_path.read_bytes())
    out = staging_path(SOURCE_ID, "gov_10a_exp.parquet")
    df.to_parquet(out, index=False)
    print(f"{len(df):,} rows -> {out}")


if __name__ == "__main__":
    main()
