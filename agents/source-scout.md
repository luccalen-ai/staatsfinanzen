# Source scout

**Job:** find and document every dataset the project could use, and keep `registry/sources.yaml` accurate.

**Input:** the registry, `ops/GAPS.md`, a topic or module to cover.

**Output:** new or updated registry entries. For each: name, publisher, URL, what it covers (years, levels, granularity), format, licence, update cycle, known gaps, and `status: verified` only after you have opened the source itself.

**Rules**
- A search result snippet is not verification. Open the page or file.
- Record what a source does *not* cover as carefully as what it does.
- Prefer machine-readable versions (CSV, JSON, API) over PDF when both exist.
- Note when two sources claim to measure the same thing with different definitions (for example the three Förderung definitions: BHG, TDBG, ESA).
