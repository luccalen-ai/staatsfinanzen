"""Public enterprise ledger: one row per publicly owned business, public money in and out.

Sources
- Bund: Beteiligungsbericht 2027 und 2028 (BMF), CSV of all holdings, extracted by
  ingest.bmf_beteiligungen to data/extracts/. Year 2025, Datenart "Erfolg" (actual cash).
  Money in = federal payments to the holding in the general budget, without UG 23 civil
  servant pensions and without "Personalämter" (pay for civil servants on loan, refunded).
  Money back = federal receipts from the holding on the same basis (dividends, refunds).
  Universities and federal museums are counted per unit; the group totals are skipped.
- Wien: Beteiligungsbericht der Stadt Wien 2024 (business year 2023), overview table of direct
  holdings, extracted by ingest.wien_beteiligungen. Money in = "Zuschüsse der Stadt Wien" (TEUR).
  The report gives no money back per company. Groups (Wien Holding, Wiener Stadtwerke, GESIBA)
  are consolidated.
- Manual rows from dossiers: registry/public_enterprises_manual.csv, merged on level + entity.

Run:  python -m models.ledger
Out:  registry/public_enterprises.csv, site/data/ledger.json
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
EXTRACTS = ROOT / "data" / "extracts"
COLUMNS = ["level", "entity", "short_name", "area", "owner", "owner_share_pct", "year",
           "public_money_in_eur", "money_back_eur", "net_cost_eur", "revenue_eur", "result_eur",
           "staff_fte", "revenue_note", "stated_public_task", "outcome_measure", "outcome_value",
           "audit_findings", "dossier", "source"]
BUND_SOURCE = ("BMF, Beteiligungsbericht 2027 und 2028, CSV, Datenstand 25.06.2026, "
               "https://www.bmf.gv.at/dam/jcr:80655f7f-dc57-4f1c-b4b9-11fbb14edc6d/Beteiligungsbericht_2027_2028.csv")
WIEN_SOURCE = ("Stadt Wien, Beteiligungsbericht 2024 (Geschäftsjahr 2023), Betriebswirtschaftliche Eckdaten, "
               "https://digital.wienbibliothek.at/download/pdf/5162233.pdf")
GENERAL = "Allgemeine Gebarung - ohne UG 23 Pensionen - Beamtinnen und Beamte"


def num_de(s: pd.Series) -> pd.Series:
    return pd.to_numeric(s.astype(str).str.replace(".", "", regex=False).str.replace(",", ".", regex=False),
                         errors="coerce")


def bund(year: str = "2025") -> pd.DataFrame:
    df = pd.read_csv(EXTRACTS / "bmf_beteiligungen_2027_2028.csv", sep=";", dtype=str, keep_default_na=False)
    df = df[~df["Gruppe_Beteiligungen"].str.contains("gesamt")]
    df["w"] = num_de(df["Wert"])
    y = df[df["Geschäftsjahr"] == year]
    fin = y[(y["Kennzahl_Kategorie"] == "Finanzkennzahl") & (y["Datenart"] == "Erfolg") & (y["Gebarung"] == GENERAL)]
    money_in = fin[fin["Kennzahl_Typ"] == "Auszahlungen"].groupby("Bezeichnung")["w"].sum()
    money_back = fin[fin["Kennzahl_Typ"] == "Einzahlungen"].groupby("Bezeichnung")["w"].sum()

    def measure(name: str) -> pd.Series:
        m = y[(y["Kennzahl_Kategorie"] == "Unternehmenskennzahl") & (y["Kennzahl_Name"] == name)]
        return m.groupby("Bezeichnung")["w"].sum(min_count=1)

    info = df.drop_duplicates("Bezeichnung").set_index("Bezeichnung")
    out = pd.DataFrame(index=info.index)
    out["level"] = "Bund"
    out["entity"] = out.index
    out["short_name"] = info["Kurzbezeichnung"]
    out["area"] = info["Bereich"]
    out["owner"] = info["Eigentümervertreter1"]
    out["owner_share_pct"] = num_de(info["Bundesanteil"]) * 100
    out["year"] = int(year)
    out["public_money_in_eur"] = money_in.reindex(out.index).fillna(0) * 1e6
    out["money_back_eur"] = money_back.reindex(out.index).fillna(0) * 1e6
    out["revenue_eur"] = measure("Umsatzerlöse").reindex(out.index) * 1e6
    out["result_eur"] = measure("Ergebnis vor Steuern").reindex(out.index) * 1e6
    out["staff_fte"] = measure("Personalstand (VZÄ)").reindex(out.index)
    out["source"] = BUND_SOURCE
    return out.reset_index(drop=True)


ROW = re.compile(r"^(?P<name>.+?)\s+(?P<res>-?[\d.]+)\s+\S\s+(?P<rev>-?[\d.]+)\s+\S\s+(?P<inv>-?[\d.]+)\s+\S\s+(?P<sub>-?[\d.]+)\s+\S$")


def wien() -> pd.DataFrame:
    text = (EXTRACTS / "wien_beteiligungsbericht" / "2024_uebersicht.txt").read_text(encoding="utf-8")
    block = text.split("TEUR Δ TEUR Δ TEUR Δ TEUR Δ", 1)[1].split("* Die Kennzahl", 1)[0]
    rows = []
    for line in block.strip().splitlines():
        m = ROW.match(line.strip())
        if not m:
            raise ValueError(f"Unparsed line in Vienna table: {line!r}")
        name = m["name"]
        note = ""
        if name.endswith("**"):
            name, note = name[:-2], "Geschäftsjahr bis 31.8."
        elif name.endswith("*"):
            name, note = name[:-1], "Umsatzerlöse enthalten öffentliche Zuschüsse"
        t = lambda s: float(s.replace(".", "")) * 1000  # noqa: E731 - TEUR to EUR
        rows.append({"level": "Wien", "entity": name.strip(), "owner": "Stadt Wien", "year": 2023,
                     "public_money_in_eur": t(m["sub"]), "revenue_eur": t(m["rev"]), "result_eur": t(m["res"]),
                     "revenue_note": note, "source": WIEN_SOURCE})
    if len(rows) != 30:
        raise ValueError(f"Expected 30 Vienna holdings, parsed {len(rows)}")
    return pd.DataFrame(rows)


def main() -> None:
    led = pd.concat([bund(), wien()], ignore_index=True)
    manual = ROOT / "registry" / "public_enterprises_manual.csv"
    m = pd.read_csv(manual, dtype=str, keep_default_na=False)
    if not m.empty:
        m = m.rename(columns={"public_money_in_eur": "public_money_in_eur"})
        led = led.set_index(["level", "entity"])
        for _, r in m.iterrows():
            key = (r.get("level", ""), r["entity"])
            for c, v in r.items():
                if v != "" and c in COLUMNS and c not in ("level", "entity"):
                    led.loc[key, c] = v
        led = led.reset_index()
    led["net_cost_eur"] = led["public_money_in_eur"] - led["money_back_eur"].fillna(0)
    led = led.reindex(columns=COLUMNS).sort_values(["level", "public_money_in_eur"], ascending=[True, False])
    led.to_csv(ROOT / "registry" / "public_enterprises.csv", index=False)
    site = ROOT / "site" / "data"
    site.mkdir(parents=True, exist_ok=True)
    rec = json.loads(led.to_json(orient="records", force_ascii=False))
    (site / "ledger.json").write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    for lvl, g in led.groupby("level"):
        print(f"{lvl}: {len(g)} entities, money in {g.public_money_in_eur.sum()/1e9:.2f} bn, "
              f"back {g.money_back_eur.fillna(0).sum()/1e9:.2f} bn, year {g.year.iloc[0]}")


if __name__ == "__main__":
    main()
