"""Offline tests for the ingest parsers and the core schema. Run: pytest -q"""

from pathlib import Path

import duckdb
import pytest

from ingest import bmf_budget_csv, eurostat_cofog

FIXTURES = Path(__file__).parent / "fixtures"
SCHEMA = Path(__file__).resolve().parents[1] / "models" / "schema.sql"


def test_schema_loads_and_seeds_units():
    con = duckdb.connect()
    con.execute(SCHEMA.read_text())
    units = dict(con.execute("SELECT unit_id, esa_subsector FROM gov_unit").fetchall())
    assert units["bund"] == "S1311"
    assert units["wien_land"] == "S1312" and units["wien_gemeinde"] == "S1313"
    # Loading twice must not fail (idempotent)
    con.execute(SCHEMA.read_text())


def test_eurostat_parse_units_and_mapping():
    df = eurostat_cofog.parse((FIXTURES / "eurostat_gov_10a_exp_sample.csv").read_bytes())
    # Empty observation is dropped
    assert len(df) == 6
    total_2024 = df[(df.geo == "AT") & (df.sector == "S13") & (df.cofog_code == "TOTAL")
                    & (df.unit == "MIO_EUR") & (df.year == 2024)].iloc[0]
    assert total_2024.amount_eur == pytest.approx(270_000_000_000)
    assert total_2024.unit_id == "at_general_government"
    assert total_2024.flag == "p"
    pct = df[(df.geo == "AT") & (df.unit == "PC_GDP")].iloc[0]
    assert pct.pct_gdp == pytest.approx(56.3) and pct.amount_eur != pct.amount_eur  # NaN
    assert set(df[df.geo == "DE"].unit_id.isna()) == {True}  # peers get no Austrian unit
    depth = dict(zip(df.cofog_code, df.cofog_depth))
    assert depth["TOTAL"] == 0 and depth["GF10"] == 1 and depth["GF1002"] == 2
    assert df[df.sector == "S1311"].unit_id.iloc[0] == "bund"


def test_eurostat_missing_column_fails():
    with pytest.raises(ValueError, match="missing columns"):
        eurostat_cofog.parse("freq,unit\nA,MIO_EUR\n")


def test_eurostat_url_contains_all_dimensions():
    url = eurostat_cofog.build_url(2015)
    assert "S1311" in url and "AT" in url and "startPeriod=2015" in url and "format=SDMX-CSV" in url


def test_bmf_parse_numbers_and_names():
    df = bmf_budget_csv.parse((FIXTURES / "bmf_budget_sample.csv").read_bytes())
    assert "geschaftsjahr" in df.columns and "betrag" in df.columns
    assert df.betrag.iloc[0] == pytest.approx(12_345_678.90)
    assert df.betrag.iloc[1] == pytest.approx(-1_000.5)
    assert df.betrag.iloc[2] == 0
    assert df.betrag.iloc[3] != df.betrag.iloc[3]  # empty -> NaN
    assert df.konto.iloc[0] == "5110.000"           # codes stay text


def test_bmf_rejects_text_in_amounts():
    bad = "Konto;Betrag\n1;abc\n"
    with pytest.raises(ValueError, match="non-numeric"):
        bmf_budget_csv.parse(bad)


def test_bmf_requires_amount_column():
    with pytest.raises(ValueError, match="No amount column"):
        bmf_budget_csv.parse("Konto;Name\n1;x\n")
