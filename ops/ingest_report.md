# Ingest report

Generated 2026-11-15 11:15 UTC by the `ingest` workflow.

## Downloaded files

| File | Bytes | SHA-256 | URL |
| --- | --- | --- | --- |
| bmf_budget_csv/2026-11-15/Bundeshaushalt_Budget_2024_bis_2028.csv | 79,957,091 | `e49cfc0606f9` | https://www.bmf.gv.at/dam/jcr:57d34c8f-f064-4499-8ea1-138d18fe21a9/Bundeshaushalt_Budget_2024_bis_2028.csv |
| eurostat_cofog/2026-11-15/gov_10a_exp.csv | 20,598,701 | `496fc8b0ea29` | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/gov_10a_exp/A.MIO_EUR+PC_GDP.S13+S1311+S1312+S1313+S1314..TE+D1+P2+D62_D632+D3+D7+P5+D9.AT+DE+NL+DK+SE+EU27_2020?format=SDMX-CSV&startPeriod=2015 |

## Staging tables

### `bmf_budget_csv/budget_2024_2028.parquet`

249,749 rows, 20 columns.

| Column | Type | Non-empty | Example values |
| --- | --- | --- | --- |
| hh | str | 249,749 | FH, EH |
| ae | str | 249,749 | 1, 2 |
| okongliederung_ebene1 | str | 249,749 | Investitionstätigkeit, Darlehen und Vorschüsse, Sachaufwand, Personalaufwand |
| okongliederung_ebene2 | str | 249,749 | Sachanlagen, Gewährte Vorschüsse, Geringwertige Wirtschaftsgüter (GWG), Sonstiger betrieblicher Sachaufwand |
| ugnr | str | 249,749 | 01, 02, 03, 04 |
| untergliederung | str | 249,749 | 01 Präsidentschaftskanzlei, 02 Bundesgesetzgebung, 03 Verfassungsgerichtshof, 04 Verwaltungsgerichtshof |
| globalbudget | str | 249,749 | 01.01 Präsidentschaftskanzlei, 02.01 Bundesgesetzgebung, 03.01 Verfassungsgerichtshof, 04.01 Verwaltungsgerichtshof |
| detailbudget1 | str | 249,749 | 01.01.01 Präsidentschaftskanzlei, 02.01.01 Nationalrat, 02.01.02 Bundesrat, 02.01.03 Klubförderung und gemeinsame Ausgab |
| detailbudget2 | str | 249,749 | 01.01.01.00 Präsidentschaftskanzlei, 02.01.01.00 Nationalrat, 02.01.02.00 Bundesrat, 02.01.03.00 Klubförderung und gemei |
| budgetposition | str | 249,749 | 01.01.01.00-1/0288.000 Hardware (ADV), 01.01.01.00-1/0420.000 Sonst. Amts-, Betriebs- und Geschäftsausstattung, 01.01.01 |
| ug_themenbereich | str | 249,749 | Sonstiges, Personal, Nationalrat, Bundesrat |
| fixvar | str | 249,749 | fix, var |
| c19flag | str | 249,749 | Auszahlungen ohne COVID-19-Krisenbewältigung, Einzahlungen ohne COVID-19 Fonds, Auszahlungen COVID-19-Krisenbewältigung, |
| forderungen | str | 249,749 | , 06 - Förderungen im Namen und auf Rechnung des Bundes, 16 - Förderungen im Namen und auf Rechnung eines externen Abwic |
| datenstand | str | 249,749 | 27.06.2025, 26.06.2026, 19.06.2025, 10.07.2026 |
| geschaftsjahr | str | 249,749 | 2024, 2025, 2026, 2027 |
| kennzahl | str | 249,749 | Erfolg, BVA |
| betrag | float64 | 249,749 | 0.0547963, 0.09423949, 0.007, 0.08432703 |
| basis | str | 249,749 | bhg |
| source_id | str | 249,749 | bmf_budget_csv |

Numeric sums: betrag = 2,809,720.53

### `eurostat_cofog/gov_10a_exp.parquet`

199,920 rows, 14 columns.

| Column | Type | Non-empty | Example values |
| --- | --- | --- | --- |
| geo | str | 199,920 | AT, DE, DK, EU27_2020 |
| year | int64 | 199,920 | 2015, 2016, 2017, 2018 |
| sector | str | 199,920 | S13, S1311, S1312, S1313 |
| unit_id | str | 19,840 | at_general_government, bund, laender, gemeinden |
| cofog_code | str | 199,920 | GF01, GF0101, GF0102, GF0103 |
| cofog_depth | int64 | 199,920 | 1, 2, 0 |
| na_item | str | 199,920 | D1, D3, D62_D632, D7 |
| unit | str | 199,920 | MIO_EUR, PC_GDP |
| value | float64 | 199,920 | 5515.3, 5694.8, 5766.6, 5968.1 |
| amount_eur | float64 | 99,960 | 5515300000.0, 5694800000.0, 5766600000.0, 5968100000.0 |
| pct_gdp | float64 | 99,960 | 1.6, 1.7, 1.5, 0.0 |
| flag | str | 5,952 | p |
| basis | str | 199,920 | esa2010 |
| consolidated | bool | 199,920 | True |

Numeric sums: year = 403,738,440.00, cofog_depth = 349,640.00, value = 1,078,581,242.20, amount_eur = 1,078,545,410,300,000.00, pct_gdp = 35,831.90
