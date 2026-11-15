# Tasks

## Phase 0 — foundation (current)

- [x] Master plan drafted
- [x] Repository structure, master prompt, agent prompts
- [x] First pass of the source registry: 32 sources, 10 opened and verified, 22 located (2026-11-15)
- [x] Vienna budget data located as CSV (offenerhaushalt.at / data.gv.at) and Förderbericht found
- [x] Machine-readable federal budget found: BMF CSV downloads replace PDF parsing
- [ ] Open each `located` source before writing its ingest script; record format, licence and update cycle
- [ ] Find the data.gv.at entries for the BMF CSVs and Vienna's files, and record their licences
- [x] Core schema in `models/schema.sql` (DuckDB), loads and seeds levels of government
- [x] First real runs on GitHub (2026-11-15): federal budget 249,749 rows, Eurostat 199,920 rows; control checks pass for federal receipts 2024 and the 2024 spending ratio
- [ ] Map BMF budget columns to the core schema (amounts are EUR million; hh = FH/EH, ae = 1 out / 2 in, kennzahl = BVA/Erfolg)
- [ ] Get Vienna's detailed VRV 2015 files (blocked by a bot check, see ops/GAPS.md)
- [ ] Start founding the Verein (statutes, board, advisory board with a public finance economist)
- [ ] Ask about research access to anonymised Transparenzdatenbank data (§ 34 Abs. 2 TDBG 2012): which institutions qualify, whether a Verein can, or which research partner could apply
- [ ] Decide licences for the project's own code and data
- [ ] Move the repository to a GitHub organisation the Verein can own

Gate to phase 1: every source used in phase 1 has a documented format, licence and update cycle.

## Phase 1 — money map (Bund and Vienna)

First ingest scripts, in this order:

1. `eurostat_cofog` — general government by function and subsector, 2019 to latest
2. `bmf_budget_csv` — federal budget by account
3. `bmf_execution_bund_laender` — Bund and Länder cash flows in one structure
4. `wien_ogd_haushalt` — Vienna accounts and budget
5. `statat_cofog` — latest official COFOG totals as control

Status: `eurostat_cofog` and `bmf_budget_csv` written with offline tests; they run in the GitHub `ingest` workflow because the development workspace cannot reach those sites.

Then:

- [ ] Reconciliation to control totals, transfers Bund–Vienna matched
- [ ] First flow diagram and treemap, private

Gate: federal and Vienna detail reconcile to control totals.

## Weekly dossiers on publicly owned businesses

- [x] Agent prompt, template and backlog set up (2026-11-15)
- [ ] First draft: Weingut Cobenzl
- [ ] Decide publication rhythm: weekly or every two weeks
