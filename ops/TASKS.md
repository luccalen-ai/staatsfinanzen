# Tasks

## Phase 0 — foundation (current)

- [x] Master plan drafted
- [x] Repository structure, master prompt, agent prompts
- [x] First pass of the source registry: 32 sources, 10 opened and verified, 22 located (2026-11-15)
- [x] Vienna budget data located as CSV (offenerhaushalt.at / data.gv.at) and Förderbericht found
- [x] Machine-readable federal budget found: BMF CSV downloads replace PDF parsing
- [ ] Open each `located` source before writing its ingest script; record format, licence and update cycle
- [ ] Find the data.gv.at entries for the BMF CSVs and Vienna's files, and record their licences
- [ ] Fix the core schema in `models/`
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

Then:

- [ ] Reconciliation to control totals, transfers Bund–Vienna matched
- [ ] First flow diagram and treemap, private

Gate: federal and Vienna detail reconcile to control totals.
