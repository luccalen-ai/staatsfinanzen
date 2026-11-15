"""BMF monthly execution, Bund and Länder (incl. Wien), current and previous year.

Cash flows (Finanzierungshaushalt) in EUR million, cumulative by month; federal data mapped to the
Länder economic classification so the two are comparable. Länder data come from Statistik Austria.

Interim source for Vienna while the detailed VRV 2015 files are not reachable automatically
(see ops/GAPS.md).

Run:  python -m ingest.bmf_execution_bund_laender
Out:  data/staging/bmf_execution_bund_laender/vollzug_bund_laender.parquet
"""

from __future__ import annotations

from ingest.bmf_budget_csv import parse
from ingest.common import download, staging_path

SOURCE_ID = "bmf_execution_bund_laender"
URL = ("https://www.bmf.gv.at/dam/jcr:fd99743f-d0ec-47b5-9a96-ef0ef81c4322/"
       "Monatlicher_Vollzug_Bund_Laender_2025_2026.csv")


def main() -> None:
    raw_path = download(SOURCE_ID, URL, "Monatlicher_Vollzug_Bund_Laender_2025_2026.csv")
    df = parse(raw_path.read_bytes())
    df["source_id"] = SOURCE_ID
    out = staging_path(SOURCE_ID, "vollzug_bund_laender.parquet")
    df.to_parquet(out, index=False)
    print(f"{len(df):,} rows, columns: {list(df.columns)} -> {out}")


if __name__ == "__main__":
    main()
