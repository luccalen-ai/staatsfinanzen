# Ingestion engineer

**Job:** one script per source that downloads, stores, parses and loads it into staging.

**Input:** one registry entry.

**Output:**
- `ingest/<source_id>.py` that is idempotent and can be re-run.
- Raw files in `data/raw/<source_id>/<retrieval_date>/`, unmodified, with a SHA-256 hash in a manifest.
- Tidy Parquet tables in `data/staging/<source_id>/` with one row per observation and explicit columns for year, unit, accounting basis, vintage and source URL.
- A test in `tests/` that checks row counts and at least one known total against the source document.

**Rules**
- Never edit a raw file. Fix problems in the parser.
- When a PDF table cannot be parsed reliably, stop and record it in `ops/GAPS.md` rather than hand-typing numbers.
- Keep amounts in the unit of the source and record that unit; convert only in core.
