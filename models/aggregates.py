"""Build small, publishable aggregates from the staging tables into site/data/*.json.

These files are what the dashboard reads. Each carries its source, year, basis and the control
total it was checked against, so a chart can always show where its numbers come from.

Run after the ingest scripts:  python -m models.aggregates
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
STAGING = ROOT / "data" / "staging"
OUT = ROOT / "site" / "data"

COFOG_DE = {
    "GF01": "Allgemeine öffentliche Verwaltung", "GF02": "Verteidigung",
    "GF03": "Öffentliche Ordnung und Sicherheit", "GF04": "Wirtschaftliche Angelegenheiten",
    "GF05": "Umweltschutz", "GF06": "Wohnungswesen und kommunale Einrichtungen",
    "GF07": "Gesundheitswesen", "GF08": "Freizeit, Sport, Kultur und Religion",
    "GF09": "Bildungswesen", "GF10": "Soziale Sicherung",
}
SECTOR_DE = {"S1311": "Bund", "S1312": "Länder", "S1313": "Gemeinden", "S1314": "Sozialversicherung"}

# VRV 2015, Anlage 2: functional groups (first digit of the Ansatz)
VRV_GRUPPE_DE = {
    "0": "Vertretungskörper und allgemeine Verwaltung", "1": "Öffentliche Ordnung und Sicherheit",
    "2": "Unterricht, Erziehung, Sport und Wissenschaft", "3": "Kunst, Kultur und Kultus",
    "4": "Soziale Wohlfahrt und Wohnbauförderung", "5": "Gesundheit",
    "6": "Straßen- und Wasserbau, Verkehr", "7": "Wirtschaftsförderung",
    "8": "Dienstleistungen", "9": "Finanzwirtschaft",
}


def write(name: str, payload: dict) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / name).write_text(json.dumps(payload, ensure_ascii=False, indent=1))
    print(f"wrote site/data/{name}")


def gesamtstaat() -> None:
    p = STAGING / "eurostat_cofog" / "gov_10a_exp.parquet"
    if not p.exists():
        return
    df = pd.read_parquet(p)
    at = df[(df.geo == "AT") & (df.na_item == "TE") & (df.unit == "MIO_EUR")]
    year = int(at[(at.sector == "S13") & (at.cofog_code == "TOTAL")].year.max())
    y = at[at.year == year]
    by_function = (y[(y.sector == "S13") & (y.cofog_depth == 1)]
                   .assign(name=lambda d: d.cofog_code.map(COFOG_DE))
                   [["cofog_code", "name", "amount_eur"]].sort_values("amount_eur", ascending=False))
    by_level = (y[(y.sector.isin(SECTOR_DE)) & (y.cofog_code == "TOTAL")]
                .assign(name=lambda d: d.sector.map(SECTOR_DE))[["sector", "name", "amount_eur"]])
    pct = df[(df.geo.isin(["AT", "DE", "NL", "DK", "SE", "EU27_2020"])) & (df.sector == "S13")
             & (df.cofog_code == "TOTAL") & (df.na_item == "TE") & (df.unit == "PC_GDP")]
    write("gesamtstaat.json", {
        "title": "Staatsausgaben Österreich nach Aufgabenbereichen",
        "source": "Eurostat gov_10a_exp (ESVG 2010), konsolidiert",
        "basis": "esa2010", "year": year,
        "total_eur": float(y[(y.sector == "S13") & (y.cofog_code == "TOTAL")].amount_eur.iloc[0]),
        "by_function": by_function.to_dict("records"),
        "by_level_unconsolidated": by_level.to_dict("records"),
        "note_levels": "Ebenen unkonsolidiert: Transfers zwischen den Ebenen sind bei beiden Seiten enthalten; die Summe ist größer als der Gesamtstaat.",
        "pct_gdp": pct[["geo", "year", "pct_gdp"]].sort_values(["geo", "year"]).to_dict("records"),
    })


def bund() -> None:
    p = STAGING / "bmf_budget_csv" / "budget_2024_2028.parquet"
    if not p.exists():
        return
    df = pd.read_parquet(p)
    out = df[(df.hh == "FH") & (df.ae == "1")]
    actual_years = sorted(int(y) for y in out[out.kennzahl == "Erfolg"].geschaftsjahr.unique())
    year = actual_years[-1]
    y = out[(out.kennzahl == "Erfolg") & (out.geschaftsjahr == str(year))]
    tree = (y.groupby(["untergliederung", "globalbudget", "detailbudget1"], as_index=False).betrag.sum()
            .assign(amount_eur=lambda d: d.betrag * 1_000_000).drop(columns="betrag"))
    by_theme = (y.groupby("ug_themenbereich", as_index=False).betrag.sum()
                .assign(amount_eur=lambda d: d.betrag * 1_000_000).drop(columns="betrag"))
    by_econ = (y.groupby("okongliederung_ebene1", as_index=False).betrag.sum()
               .assign(amount_eur=lambda d: d.betrag * 1_000_000).drop(columns="betrag"))
    foerd = y[y.forderungen.str.strip() != ""]
    write("bund.json", {
        "title": "Auszahlungen des Bundes",
        "source": "BMF, Bundeshaushalt Budget 2024 bis 2028 (CSV)",
        "basis": "bhg_cash", "stage": "actual", "year": year,
        "total_eur": float(y.betrag.sum() * 1_000_000),
        "tree": tree.to_dict("records"),
        "by_theme": by_theme.sort_values("amount_eur", ascending=False).to_dict("records"),
        "by_economic": by_econ.sort_values("amount_eur", ascending=False).to_dict("records"),
        "foerderungen_eur": float(foerd.betrag.sum() * 1_000_000),
    })


def wien() -> None:
    p = STAGING / "wien_ogd_haushalt" / "wien_vrv2015.parquet"
    if not p.exists():
        return
    df = pd.read_parquet(p)
    ra = df[(df.voranschlag_rechnungsabschluss == "Rechnungsabschluss") & (df.datenquelle == "Gemeinde")
            & (df.haushalt == "Finanzierungshaushalt") & df.mvag.str.match("3[246]")]
    year = int(ra.jahr.astype(int).max())
    all_y = ra[ra.jahr.astype(int) == year]
    financing = all_y[all_y.mvag.str.startswith("36")]          # repayments of debt etc., not spending
    y = all_y[all_y.mvag.str.match("3[24]")].assign(gruppe=lambda d: d.ansatz_uab.str[0])
    ra = ra[ra.mvag.str.match("3[24]")]
    tree = (y.groupby(["gruppe", "ansatz_uab", "ansatz_text"], as_index=False).wert.sum()
            .rename(columns={"wert": "amount_eur"}))
    tree["gruppe_name"] = tree.gruppe.map(VRV_GRUPPE_DE)
    trend = (ra.assign(jahr=ra.jahr.astype(int), gruppe=ra.ansatz_uab.str[0])
             .groupby(["jahr", "gruppe"], as_index=False).wert.sum()
             .rename(columns={"wert": "amount_eur"}))
    trend["gruppe_name"] = trend.gruppe.map(VRV_GRUPPE_DE)
    write("wien.json", {
        "title": "Auszahlungen der Stadt Wien",
        "source": "Stadt Wien, Rechnungsabschluss nach VRV 2015, über offenerhaushalt.at (CC BY 4.0)",
        "basis": "vrv2015_cash", "stage": "actual", "year": year,
        "total_eur": float(y.wert.sum()),
        "total_incl_financing_eur": float(all_y.wert.sum()),
        "financing_outflows_eur": float(financing.wert.sum()),
        "definition": "Operative und investive Auszahlungen (MVAG 32 und 34). Auszahlungen aus der Finanzierungstätigkeit (MVAG 36, v. a. Tilgungen) sind separat ausgewiesen.",
        "note": "Gesamthaushalt der Bundeshauptstadt Wien (Land und Gemeinde gemeinsam). Unternehmungen mit eigenem Abschluss (z. B. Wiener Wohnen) und Beteiligungen sind nur mit den Zahlungen der Stadt an sie enthalten.",
        "tree": tree[tree.amount_eur > 0].sort_values("amount_eur", ascending=False).to_dict("records"),
        "trend_by_group": trend.to_dict("records"),
    })


def main() -> None:
    gesamtstaat()
    bund()
    wien()


if __name__ == "__main__":
    main()
