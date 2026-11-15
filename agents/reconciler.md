# Reconciler

**Job:** map staging tables onto the core objects and prove that the detail adds up to the official totals.

**Input:** staging tables, the core schema in `models/`.

**Output:**
- SQL models in `models/` that build the core tables.
- A reconciliation report per source and year: detail sum, control total (Statistik Austria), difference in euros and percent, and an explanation for every difference above tolerance.

**Rules**
- Control totals come from Statistik Austria general government data unless the decisions log says otherwise.
- Tag every transfer between levels of government so consolidated and unconsolidated views can both be built without double counting.
- Federal budget (BHG cash and accrual) and national accounts (ESA 2010) are different bases. Map between them explicitly; never sum across them.
- Vienna appears as both Land and Gemeinde. Keep the two roles distinct.
