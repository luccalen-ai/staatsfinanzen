# Ingest report

Generated 2026-11-15 12:04 UTC by the `ingest` workflow.

## Downloaded files

| File | Bytes | SHA-256 | URL |
| --- | --- | --- | --- |
| bmf_budget_csv/2026-11-15/Bundeshaushalt_Budget_2024_bis_2028.csv | 79,957,091 | `e49cfc0606f9` | https://www.bmf.gv.at/dam/jcr:57d34c8f-f064-4499-8ea1-138d18fe21a9/Bundeshaushalt_Budget_2024_bis_2028.csv |
| bmf_execution_bund_laender/2026-11-15/Monatlicher_Vollzug_Bund_Laender_2025_2026.csv | 356,092 | `fe8d1755f366` | https://www.bmf.gv.at/dam/jcr:fd99743f-d0ec-47b5-9a96-ef0ef81c4322/Monatlicher_Vollzug_Bund_Laender_2025_2026.csv |
| eurostat_cofog/2026-11-15/gov_10a_exp.csv | 20,598,701 | `496fc8b0ea29` | https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/gov_10a_exp/A.MIO_EUR+PC_GDP.S13+S1311+S1312+S1313+S1314..TE+D1+P2+D62_D632+D3+D7+P5+D9.AT+DE+NL+DK+SE+EU27_2020?format=SDMX-CSV&startPeriod=2015 |

## Control totals

| Check | Expected | Parsed | Difference | Result |
| --- | --- | --- | --- | --- |
| bund_fh_einzahlungen_2024 | 101,568,000,000.0 | 101,567,892,541.0 | -0.00% | pass |
| gesamtstaat_ausgaben_2025 | 283,000,000,000.0 | no matching rows | | skipped |
| gesamtstaat_ausgabenquote_2025 | 55.2 | no matching rows | | skipped |
| gesamtstaat_ausgabenquote_2024 | 55.3 | 55.2 | -0.18% | pass |
| wien_auszahlungen_2024 | 19,930,000,000.0 | 19,931,924,538.9 | +0.01% | pass |
| wien_einzahlungen_2024 | 19,980,000,000.0 | 19,981,655,418.4 | +0.01% | pass |

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

### `bmf_execution_bund_laender/vollzug_bund_laender.parquet`

2,303 rows, 13 columns.

| Column | Type | Non-empty | Example values |
| --- | --- | --- | --- |
| ae | str | 2,303 | 2, 1 |
| b_l | str | 2,303 | Länder (inkl. Wien), Bund |
| verwaltungseinheit | str | 2,303 | Burgenland, Kärnten, Niederösterreich, Oberösterreich |
| okongliederung_lander_1 | str | 2,303 | Operative Gebarung, Investive Gebarung, nicht definiert |
| okongliederung_lander_2 | str | 2,303 | Operative Verwaltungstätigkeit, Investitionstätigkeit, Darlehen und Vorschüsse, Transfers |
| datenstand | str | 2,303 | 30.10.2026, 30.09.2026, 31.08.2026, 31.07.2026 |
| quelle | str | 2,303 | Statistik Austria, BMF |
| geschaftsjahr | str | 2,303 | 2026, 2025 |
| monate_kumuliert | str | 2,303 | Jänner-September, Jänner-August, Jänner-Juli, Jänner-Juni |
| kennzahl | str | 2,303 | kumulierter Monatserfolg |
| betrag | float64 | 2,303 | 676.74368917, 28.74958095, 14.14257792, 527.9474118 |
| basis | str | 2,303 | bhg |
| source_id | str | 2,303 | bmf_execution_bund_laender |

Numeric sums: betrag = 2,509,396.55

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

### `wien_ogd_haushalt/wien_vrv2015.parquet`

221,974 rows, 25 columns.

| Column | Type | Non-empty | Example values |
| --- | --- | --- | --- |
| jahr | str | 221,974 | 2020, 2021, 2022, 2023 |
| bundesland | str | 221,974 | Wien |
| voranschlag_rechnungsabschluss | str | 221,974 | Rechnungsabschluss, Voranschlag |
| datenquelle | str | 221,974 | Gemeinde, Statistik Austria |
| gemeindekennziffer | str | 221,974 | 90001 |
| gemeindename | str | 221,974 | Wien |
| haushalt | str | 221,974 | Ergebnishaushalt, Finanzierungshaushalt, Vermögenshaushalt |
| ansatz_uab | str | 221,974 | 000, 010, 011, 014 |
| ansatz_ugl | str | 221,974 | 100, 300, 400, 500 |
| konto_grp | str | 221,974 | 452, 453, 621, 721 |
| konto_ugl | str | 221,974 | 000, 001, 002, 003 |
| vorhabencode | str | 221,974 | 0000000 |
| mvag | str | 221,974 | 2221, 2222, 2225, 2234 |
| ansatz_text | str | 221,974 | Vertretung der Stadt, Europäische Angelegenheiten, Krisenmanagement und Sofortmaßnahmen, Verwaltungsstrafen |
| konto_text | str | 221,974 | Treibstoffe, Diverse, Schmier- und Schleifmittel, Diverse, Sonstige Transporte, Diverse, Bezüge (gewählte Organe) |
| wert | float64 | 190,615 | 9689.35, 0.0, 19734.47, 142264.46 |
| doc_id | str | 221,974 | wien_ogd_haushalt/2026-11-15/offenerhaushalt_90001_2020_ra_ehh_gemeinde.csv, wien_ogd_haushalt/2026-11-15/offenerhaushal |
| id_vhh | float64 | 30,997 | 94101400.0, 99000000.0, 99000030.0, 98000000.0 |
| sektor | str | 31,359 | 0000, 1311, 1313, 1400 |
| land | str | 31,359 | AT |
| endstand_vj | float64 | 31,359 | 0.0, -1248119.68, 85966.98, 180777.55 |
| zugang | float64 | 31,359 | 783.83, 0.0, 570.12, 1250.0 |
| abgang | float64 | 31,359 | 0.0, 1303147771.57, 101029.11, 84918.91 |
| aenderung | float64 | 31,359 | 0.0, 9652817.05, 22446.8, 3481153.55 |
| endstand_rj | float64 | 31,359 | 783.83, -1303147771.57, 570.12, -1248119.68 |

Numeric sums: wert = 1,422,895,429,934.83, id_vhh = 129,387,265,446,112,416.00, endstand_vj = 399,918,602,012.46, zugang = 2,407,967,513,012.21, abgang = 2,393,954,273,992.92, aenderung = 6,316,923,239.90, endstand_rj = 415,937,767,538.62
