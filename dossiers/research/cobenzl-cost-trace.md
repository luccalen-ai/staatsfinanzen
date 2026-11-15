# Weingut Cobenzl: where the costs sit (research note, 2026-11-15)

Working note for the dossier draft. Figures from Vienna's VRV 2015 accounts (Rechnungsabschluss,
source "Gemeinde", offenerhaushalt.at, CC BY 4.0), staged in
`data/staging/wien_ogd_haushalt/wien_vrv2015.parquet`. Queries are reproducible with DuckDB.
Nothing below is an allegation: each point is a place where cost or value does not appear in the
winery's own line, and a question to ask.

## 1. No accounts of its own

The winery is run inside MA 49 (Forst- und Landwirtschaftsbetrieb), not as a company. It has no
annual accounts, no Firmenbuch filing and no entry in the city's Beteiligungsbericht. In the budget
it shares Ansatz 862 "Landwirtschaftsbetrieb" with all of MA 49's farms. The accounts never name
Cobenzl or the winery.

Ansatz 862, cash, EUR m:

| Year | Operating receipts | Operating payments | Balance | Investment out | Goods sold (808) |
| --- | --- | --- | --- | --- | --- |
| 2020 | 4.98 | 6.40 | -1.42 | 0.89 | 3.36 |
| 2021 | 5.54 | 5.66 | -0.12 | 2.02 | 3.85 |
| 2022 | 6.23 | 6.70 | -0.47 | 2.97 | 4.04 |
| 2023 | 6.02 | 7.01 | -0.99 | 0.56 | 3.98 |
| 2024 | 5.67 | 6.58 | -0.91 | 0.29 | 3.85 |
| 2025 | 4.97 | 5.87 | -0.90 | 1.05 | 3.12 |

## 2. Capital tied up, not costed

Ansatz 862 carries EUR 414.8 m of land at end 2025 (unbuilt 378.7, built 36.1) and buildings at a gross
EUR 34.3 m, EUR 2.9 m net of EUR 31.45 m write-downs: EUR 417.7 m net. (Corrected 2026-11-15: an
earlier version gave EUR 449.1 m as book value; that was the gross figure.) The cash view charges nothing for using them; the
accrual view charges only depreciation (EUR 0.49 m in 2025). The winery's share of these assets is
not stated. A market comparison (lease value of vineyard land in Grinzing and on the Bisamberg)
would show the cost of the capital the city provides free.

## 3. Large asset movements

2025: EUR 21.24 m of unbuilt land left Ansatz 862, the accrual account shows EUR 17.87 m
"Verluste aus dem Abgang von Sachanlagen", and cash receipts from land sales were EUR 1.92 m.
2022: EUR 15.98 m investment receipts (land sales). Could be sales below book value or transfers
to other departments; the accounts do not say. Question for MA 49 / MA 5.

## 4. The Cobenzl site is booked on a different line

The press reported that the city paid the former operator of the neighbouring Schloss Cobenzl
site about EUR 13.5 m for its building investments. In the accounts, Ansatz 866 "Stadtforste"
(forestry, not farms) shows a EUR 13.59 m payment for "Gebäude und Bauten" in 2024. The 2024
budget for that line planned EUR 16.53 m of investment, so the payment was budgeted at line level,
though not under the buildings account. Lease income on Ansatz 866 rose from EUR 1.27 m (2020) to
EUR 2.72 m (2025). The match of the EUR 13.59 m with the Cobenzl payment is likely but not
confirmed: ask MA 49.

Note: Schloss Cobenzl (café and events) is a separate operation from the winery. The dossier
must keep them apart while showing the full public cost of the Cobenzl site.

## 5. Costs carried centrally

- Pensions of retired civil servants are booked in collective lines (Ansatz 026 "Sammelansatz
  Geschäftsgruppe ..."), not on 862. Ansatz 862 shows no civil servant pay in 2025.
- Internal services are charged only in part: "Leistungen der MA 6" and "MA 01" total about
  EUR 0.05 m on 862 in 2025. IT, legal, procurement and building management by other departments
  are mostly not allocated.
- MA 49's management and forestry staff sit on Ansatz 866 (personnel EUR 27.8 m in 2025).

## 6. Revenue that may be public money

Sales of goods (EUR 3.1-4.0 m a year) may include wine bought by the city itself for receptions
and gifts. Such purchases would show as revenue on 862 and as cost elsewhere. Ask for the share
of sales to city departments and city companies.

## 7. Related holdings on the same line

The city's stake in Österreich Wein Marketing GmbH is held under Ansatz 862 (EUR 0.87 m of
"sonstige Beteiligungen" on the line). ÖWM reported a result of EUR -3.8 m in 2023.

## Questions for an information request (draft, not sent)

1. Revenue, costs and staff of the winery alone, 2019-2025, including allocated overheads.
2. Area and book value of the winery's vineyards and buildings.
3. Sales by customer group, including city departments and city companies.
4. The EUR 13.59 m payment on Ansatz 866 in 2024: recipient and purpose.
5. The 2025 land disposals on Ansatz 862: buyer or receiving department, price and book value.
6. The lease terms for Schloss Cobenzl since the operator change, including minimum rent.
