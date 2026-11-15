"""Cost trace for one or more Vienna budget lines (Ansätze), from the VRV 2015 accounts.

Seven checks, each printed as a Markdown section with the numbers behind it:
  1. Cash by year: operating receipts and payments, investment in and out, budget against actual.
  2. Accrual by year: income, personnel, other expense (incl. depreciation, disposal losses), result.
  3. Assets: land, buildings and other fixed assets at year end; additions and disposals.
  4. Disposals: disposal losses (accrual) set against cash from asset sales.
  5. Matching amounts: payments anywhere in the accounts within a tolerance of amounts named
     in the public record (press, council), to find where a one-off was booked.
  6. Central costs: civil servant pay on the line (if none, pensions and pay sit centrally) and
     internal charges from service departments.
  7. Holdings and other items booked on the line (participations, guarantees).

Run:  python -m analysis.cost_trace --ansatz 862 --related 866 --amount 13.5e6 --out dossiers/research/x.md
The staging table comes from `python -m ingest.wien_haushalt --manual`.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
TABLE = ROOT / "data" / "staging" / "wien_ogd_haushalt" / "wien_vrv2015.parquet"
SOURCE = ("Stadt Wien, Rechnungsabschlüsse und Voranschläge nach VRV 2015, Quelle Gemeinde, "
          "über offenerhaushalt.at (KDZ), CC BY 4.0")


def con(table: Path | str = TABLE) -> duckdb.DuckDBPyConnection:
    c = duckdb.connect()
    c.sql(f"create view v as select *, cast(jahr as int) as y from '{table}' where datenquelle = 'Gemeinde'")
    return c


def md(df: pd.DataFrame) -> str:
    if "year" in df.columns:
        df = df.assign(year=df["year"].astype("Int64").astype(str))
    return df.to_markdown(index=False, floatfmt=".2f") if not df.empty else "_No rows._"


def in_list(ansaetze: list[str]) -> str:
    return ", ".join(f"'{a}'" for a in ansaetze)


def cash(c, a: str) -> pd.DataFrame:
    return c.sql(f"""
      select y as year, voranschlag_rechnungsabschluss as basis,
        round(sum(case when mvag like '31%' then wert end)/1e6, 2) as op_in_m,
        round(sum(case when mvag like '32%' then wert end)/1e6, 2) as op_out_m,
        round(sum(case when mvag like '31%' then wert else 0 end)/1e6
            - sum(case when mvag like '32%' then wert else 0 end)/1e6, 2) as op_balance_m,
        round(sum(case when mvag like '33%' then wert end)/1e6, 2) as inv_in_m,
        round(sum(case when mvag like '34%' then wert end)/1e6, 2) as inv_out_m
      from v where ansatz_uab in ({a}) and haushalt = 'Finanzierungshaushalt'
      group by all order by year, basis""").df()


def accrual(c, a: str) -> pd.DataFrame:
    return c.sql(f"""
      select y as year,
        round(sum(case when mvag like '21%' then wert end)/1e6, 2) as income_m,
        round(sum(case when mvag like '221%' then wert end)/1e6, 2) as personnel_m,
        round(sum(case when mvag like '222%' then wert end)/1e6, 2) as other_expense_m,
        round(sum(case when mvag like '2226%' and konto_text ilike '%abschreibung%' then wert end)/1e6, 2) as depreciation_m,
        round(sum(case when konto_text ilike 'Verluste aus dem Abgang%' then wert end)/1e6, 2) as disposal_loss_m,
        round(sum(case when mvag like '21%' then wert else 0 end)/1e6
            - sum(case when mvag like '22%' then wert else 0 end)/1e6, 2) as result_m
      from v where ansatz_uab in ({a}) and haushalt = 'Ergebnishaushalt'
        and voranschlag_rechnungsabschluss = 'Rechnungsabschluss'
      group by all order by year""").df()


def assets(c, a: str) -> pd.DataFrame:
    """Year-end values. Gross values are reduced by the write-down accounts (Wertberichtigungen,
    Kontengruppen 091-098), so land, buildings and other fixed assets are net values."""
    return c.sql(f"""
      select y as year,
        round(sum(case when konto_grp in ('000','001','002','091') then endstand_rj end)/1e6, 1) as land_net_m,
        round(sum(case when konto_grp like '01%' then endstand_rj end)/1e6, 1) as buildings_gross_m,
        round(sum(case when konto_grp like '01%' or konto_grp in ('092','097') then endstand_rj end)/1e6, 1) as buildings_net_m,
        round(sum(case when konto_grp between '020' and '079' or konto_grp in ('093','094','095','096','098') then endstand_rj end)/1e6, 1) as other_fixed_net_m,
        round(sum(case when konto_grp between '000' and '079' then zugang end)/1e6, 2) as additions_m,
        round(sum(case when konto_grp between '000' and '079' then abgang end)/1e6, 2) as disposals_m,
        round(sum(case when konto_text ilike 'Vermögensübertragung innerhalb%' then endstand_rj end)/1e6, 2) as transfers_within_admin_m,
        round(sum(case when konto_grp between '080' and '089' then endstand_rj end)/1e6, 2) as holdings_m
      from v where ansatz_uab in ({a}) and haushalt = 'Vermögenshaushalt'
        and voranschlag_rechnungsabschluss = 'Rechnungsabschluss'
      group by all order by year""").df()


def disposals(c, a: str) -> pd.DataFrame:
    return c.sql(f"""
      with acc as (select y, sum(wert) loss from v where ansatz_uab in ({a}) and haushalt='Ergebnishaushalt'
                     and voranschlag_rechnungsabschluss='Rechnungsabschluss' and konto_text ilike 'Verluste aus dem Abgang%' group by y),
           gain as (select y, sum(wert) gain from v where ansatz_uab in ({a}) and haushalt='Ergebnishaushalt'
                     and voranschlag_rechnungsabschluss='Rechnungsabschluss' and konto_text ilike 'Gewinne aus dem Abgang%' group by y),
           cashin as (select y, sum(wert) cash from v where ansatz_uab in ({a}) and haushalt='Finanzierungshaushalt'
                     and voranschlag_rechnungsabschluss='Rechnungsabschluss' and mvag like '331%' group by y),
           book as (select y, sum(abgang) out_book from v where ansatz_uab in ({a}) and haushalt='Vermögenshaushalt'
                     and konto_grp between '000' and '079' group by y)
      select coalesce(acc.y, gain.y, cashin.y, book.y) as year,
        round(book.out_book/1e6, 2) as assets_off_books_m, round(cashin.cash/1e6, 2) as cash_from_sales_m,
        round(acc.loss/1e6, 2) as disposal_loss_m, round(gain.gain/1e6, 2) as disposal_gain_m
      from acc full join gain using (y) full join cashin using (y) full join book using (y)
      order by year""").df()


def matching(c, amounts: list[float], tol: float) -> pd.DataFrame:
    if not amounts:
        return pd.DataFrame()
    cond = " or ".join(f"abs(wert - {x}) <= {x * tol}" for x in amounts)
    return c.sql(f"""
      select y as year, ansatz_uab, ansatz_text, mvag, konto_text, round(wert/1e6, 2) as amount_m
      from v where haushalt = 'Finanzierungshaushalt' and voranschlag_rechnungsabschluss = 'Rechnungsabschluss'
        and mvag like '3%' and mvag not like '36%' and ({cond})
        and ansatz_uab not like '05%' and konto_text not ilike '%Pension%' and konto_text not ilike '%Geldbezüge%'
      order by year, ansatz_uab""").df()


def central(c, a: str) -> pd.DataFrame:
    return c.sql(f"""
      select y as year,
        round(sum(case when konto_text ilike '%Beamt%' and mvag like '32%' then wert end)/1e6, 2) as civil_servant_pay_m,
        round(sum(case when mvag like '32%' and (konto_text ilike '%Leistungen der MA%' or konto_text ilike '%MA %Leistung%') then wert end)/1e6, 2) as internal_charges_m,
        round(sum(case when konto_text ilike '%Pension%' then wert end)/1e6, 2) as pensions_on_line_m
      from v where ansatz_uab in ({a}) and haushalt = 'Finanzierungshaushalt'
        and voranschlag_rechnungsabschluss = 'Rechnungsabschluss'
      group by all order by year""").df()


def holdings(c, a: str) -> pd.DataFrame:
    return c.sql(f"""
      select distinct konto_grp, konto_text from v
      where ansatz_uab in ({a}) and haushalt = 'Vermögenshaushalt'
        and (konto_grp between '080' and '089' or konto_text ilike '%Haftung%' or konto_text ilike '%GmbH%')
      order by konto_grp""").df()


def trace(ansatz: list[str], related: list[str], amounts: list[float], tol: float = 0.02, table: Path | str = TABLE) -> str:
    c = con(table)
    a = in_list(ansatz)
    names = c.sql(f"select distinct ansatz_uab, ansatz_text from v where ansatz_uab in ({in_list(ansatz + related)}) order by 1").df()
    out = [f"# Cost trace: Ansatz {', '.join(ansatz)}", "", f"Source: {SOURCE}. Amounts in EUR million.", "",
           md(names), "",
           "## 1. Cash, budget (Voranschlag) against actual (Rechnungsabschluss)", "", md(cash(c, a)), "",
           "## 2. Accrual result", "", md(accrual(c, a)), "",
           "## 3. Assets on the line (net of write-downs; buildings also gross)", "", md(assets(c, a)), "",
           "## 4. Disposals: book value off, cash in, loss or gain", "", md(disposals(c, a)), "",
           f"## 5. Payments matching amounts from the public record (±{tol:.0%})", "", md(matching(c, amounts, tol)), "",
           "## 6. Costs carried centrally", "",
           "If civil servant pay is zero, any civil servants' pay and all pensions sit in collective lines.", "",
           md(central(c, a)), "",
           "## 7. Holdings and other items on the line", "", md(holdings(c, a)), ""]
    for r in related:
        out += [f"## Related line {r}: cash", "", md(cash(c, f"'{r}'")), "",
                f"## Related line {r}: assets", "", md(assets(c, f"'{r}'")), ""]
    return "\n".join(out)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--ansatz", nargs="+", required=True)
    p.add_argument("--related", nargs="*", default=[])
    p.add_argument("--amount", nargs="*", type=float, default=[])
    p.add_argument("--tol", type=float, default=0.02)
    p.add_argument("--out")
    args = p.parse_args()
    text = trace(args.ansatz, args.related, args.amount, args.tol)
    if args.out:
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"Written to {args.out}")
    else:
        print(text)


if __name__ == "__main__":
    main()
