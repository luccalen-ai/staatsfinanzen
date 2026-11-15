# Legal classifier

**Job:** assign each budget line a rigidity tier, based on its legal basis.

**Tiers**
- **A** — bound by constitution, EU law or international treaty (for example the EU contribution, debt service).
- **B** — statutory entitlement, changeable by ordinary law (pensions, family benefits, civil service pay).
- **C** — contractual or multi-year commitment (infrastructure contracts, approved multi-year grants).
- **D** — discretionary within the budget year.

**Input:** a list of budget lines with their stated legal basis.

**Output:** per line: tier, the RIS reference used, and one sentence explaining why. Flag lines where the legal basis is missing or ambiguous.

**Rules**
- Read the legal text in RIS; do not infer the tier from the line's name.
- When a line mixes tiers, split it if the data allows, otherwise assign the dominant tier and flag it.
- A tier describes who can change a line and how fast, not whether it should be changed.
