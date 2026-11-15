-- Core schema, DuckDB.
-- Every amount row links to the source document it came from (doc_id).
-- Amounts are stored in EUR (not thousands or millions); the ingest layer converts.

-- ---------- Provenance ----------

CREATE TABLE IF NOT EXISTS source_document (
    doc_id        VARCHAR PRIMARY KEY,      -- <source_id>/<retrieval_date>/<file name>
    source_id     VARCHAR NOT NULL,         -- id in registry/sources.yaml
    url           VARCHAR NOT NULL,
    retrieved_at  TIMESTAMP NOT NULL,
    sha256        VARCHAR NOT NULL,
    vintage       VARCHAR                   -- the source's own data date or edition
);

-- ---------- Dimensions ----------

-- Any public body that spends or receives: Bund, a Land, a Gemeinde, a social insurance fund,
-- an extra-budgetary unit, an enterprise without legal personality (Unternehmung, Betrieb), etc.
-- Vienna appears twice: as Land (wien_land) and as Gemeinde (wien_gemeinde).
CREATE TABLE IF NOT EXISTS gov_unit (
    unit_id         VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL,
    level           VARCHAR NOT NULL CHECK (level IN
                      ('bund', 'land', 'gemeinde', 'social_security', 'extrabudgetary', 'eu', 'international', 'other')),
    esa_subsector   VARCHAR,                -- S1311, S1312, S1313, S1314 where applicable
    parent_unit_id  VARCHAR REFERENCES gov_unit (unit_id)
);

CREATE TABLE IF NOT EXISTS cofog (
    code        VARCHAR PRIMARY KEY,        -- GF01, GF0101, ... as used by Eurostat; TOTAL for the total
    parent_code VARCHAR,
    depth       INTEGER NOT NULL,           -- 0 total, 1 division, 2 group
    name_de     VARCHAR,
    name_en     VARCHAR
);

CREATE TABLE IF NOT EXISTS legal_basis (
    legal_basis_id VARCHAR PRIMARY KEY,
    ris_reference  VARCHAR,                 -- RIS Gesetzesnummer or URL
    title          VARCHAR,
    kind           VARCHAR                  -- constitution, eu_law, treaty, federal_law, land_law, regulation, contract, guideline
);

-- A line of a budget as published by its owner (federal account, Vienna Ansatz/Post, ...)
CREATE TABLE IF NOT EXISTS budget_line (
    line_id         VARCHAR PRIMARY KEY,    -- <unit_id>:<code>
    unit_id         VARCHAR NOT NULL REFERENCES gov_unit (unit_id),
    code            VARCHAR NOT NULL,       -- e.g. federal UG.GB.DB.account
    name            VARCHAR,
    parent_line_id  VARCHAR,
    cofog_code      VARCHAR REFERENCES cofog (code),
    legal_basis_id  VARCHAR REFERENCES legal_basis (legal_basis_id),
    rigidity_tier   VARCHAR CHECK (rigidity_tier IN ('A', 'B', 'C', 'D')),
    rigidity_reason VARCHAR
);

-- ---------- Facts ----------

-- One amount, fully labelled. Long format: every dimension is a column, many may be NULL.
CREATE TABLE IF NOT EXISTS fact_amount (
    fact_id         VARCHAR PRIMARY KEY,
    year            INTEGER NOT NULL,
    period          VARCHAR,                -- NULL for annual, else 'M01'..'M12' or 'Q1'..'Q4'
    unit_id         VARCHAR REFERENCES gov_unit (unit_id),
    line_id         VARCHAR REFERENCES budget_line (line_id),
    cofog_code      VARCHAR REFERENCES cofog (code),
    esa_transaction VARCHAR,                -- TE total expenditure, D1 compensation of employees, ...
    direction       VARCHAR NOT NULL CHECK (direction IN ('expenditure', 'revenue', 'balance', 'stock')),
    amount_eur      DOUBLE NOT NULL,
    basis           VARCHAR NOT NULL CHECK (basis IN
                      ('esa2010', 'bhg_cash', 'bhg_accrual', 'vrv2015_cash', 'vrv2015_accrual', 'other')),
    stage           VARCHAR NOT NULL CHECK (stage IN
                      ('draft', 'plan', 'preliminary', 'actual', 'audited', 'forecast')),
    consolidated    BOOLEAN,
    confidence      VARCHAR NOT NULL CHECK (confidence IN ('official', 'parsed', 'derived', 'estimated')),
    doc_id          VARCHAR NOT NULL REFERENCES source_document (doc_id)
);

-- Money moving between two parties. Transfers between levels of government are tagged so that
-- consolidated views count each euro once.
CREATE TABLE IF NOT EXISTS flow (
    flow_id       VARCHAR PRIMARY KEY,
    year          INTEGER NOT NULL,
    from_unit_id  VARCHAR REFERENCES gov_unit (unit_id),
    to_unit_id    VARCHAR REFERENCES gov_unit (unit_id),
    to_entity_id  VARCHAR,                  -- public_entity or recipient, when the receiver is not a gov_unit
    flow_type     VARCHAR NOT NULL,         -- intergov_transfer, eu_contribution, eu_return, oda, subsidy, capital_injection, lease, compensation, ...
    amount_eur    DOUBLE NOT NULL,
    basis         VARCHAR NOT NULL,
    confidence    VARCHAR NOT NULL,
    doc_id        VARCHAR NOT NULL REFERENCES source_document (doc_id)
);

-- ---------- Förderungen ----------

CREATE TABLE IF NOT EXISTS programme (
    programme_id    VARCHAR PRIMARY KEY,
    name            VARCHAR NOT NULL,
    funder_unit_id  VARCHAR REFERENCES gov_unit (unit_id),
    definition      VARCHAR NOT NULL CHECK (definition IN ('bhg', 'tdbg', 'esa', 'wien_ftg', 'other')),
    goal            VARCHAR,
    target_group    VARCHAR,
    cofog_code      VARCHAR REFERENCES cofog (code),
    legal_basis_id  VARCHAR REFERENCES legal_basis (legal_basis_id),
    is_tax_expenditure BOOLEAN DEFAULT FALSE,
    evaluation_url  VARCHAR
);

CREATE TABLE IF NOT EXISTS programme_amount (
    programme_id VARCHAR NOT NULL REFERENCES programme (programme_id),
    year         INTEGER NOT NULL,
    kind         VARCHAR NOT NULL CHECK (kind IN ('budgeted', 'paid', 'forgone_revenue')),
    amount_eur   DOUBLE NOT NULL,
    cases        INTEGER,
    confidence   VARCHAR NOT NULL,
    doc_id       VARCHAR NOT NULL REFERENCES source_document (doc_id),
    PRIMARY KEY (programme_id, year, kind, doc_id)
);

-- ---------- Public enterprises (for the weekly dossiers) ----------

-- Companies and enterprises owned by a public body: GmbHs, AGs, funds, and enterprises inside the
-- administration without their own legal personality (e.g. a city-run winery).
CREATE TABLE IF NOT EXISTS public_entity (
    entity_id        VARCHAR PRIMARY KEY,
    name             VARCHAR NOT NULL,
    legal_form       VARCHAR,               -- GmbH, AG, Anstalt, Fonds, Unternehmung, Betrieb (no legal personality), ...
    firmenbuch_nr    VARCHAR,
    owner_unit_id    VARCHAR REFERENCES gov_unit (unit_id),
    ownership_share  DOUBLE,                -- 0..1, direct share of owner_unit_id
    parent_entity_id VARCHAR,               -- for indirect holdings (e.g. via Wien Holding)
    sector           VARCHAR,
    in_government_sector BOOLEAN            -- classified inside S13 by Statistik Austria
);

CREATE TABLE IF NOT EXISTS entity_financials (
    entity_id   VARCHAR NOT NULL REFERENCES public_entity (entity_id),
    year        INTEGER NOT NULL,
    item        VARCHAR NOT NULL,           -- revenue, result, equity, debt, employees, public_transfers_received, ...
    amount      DOUBLE NOT NULL,
    unit        VARCHAR NOT NULL,           -- EUR, persons, ...
    confidence  VARCHAR NOT NULL,
    doc_id      VARCHAR NOT NULL REFERENCES source_document (doc_id),
    PRIMARY KEY (entity_id, year, item, doc_id)
);

-- ---------- Findings ----------

CREATE TABLE IF NOT EXISTS finding (
    finding_id    VARCHAR PRIMARY KEY,
    title_de      VARCHAR NOT NULL,
    claim         VARCHAR NOT NULL,
    category      VARCHAR NOT NULL CHECK (category IN
                    ('irregularity', 'duplication', 'inefficiency', 'political_priority', 'context')),
    amount_eur    DOUBLE,
    amount_year   INTEGER,
    rigidity_tier VARCHAR CHECK (rigidity_tier IN ('A', 'B', 'C', 'D')),
    origin        VARCHAR NOT NULL,         -- rechnungshof, fiskalrat, budgetdienst, wifo, ihs, own_analysis, ...
    status        VARCHAR NOT NULL CHECK (status IN
                    ('candidate', 'verified', 'rejected', 'published', 'implemented', 'partly_implemented', 'not_implemented')),
    verified_at   TIMESTAMP,
    doc_id        VARCHAR REFERENCES source_document (doc_id)
);

CREATE TABLE IF NOT EXISTS finding_link (
    finding_id  VARCHAR NOT NULL REFERENCES finding (finding_id),
    object_type VARCHAR NOT NULL,           -- gov_unit, budget_line, programme, public_entity, flow
    object_id   VARCHAR NOT NULL,
    PRIMARY KEY (finding_id, object_type, object_id)
);

-- ---------- Seed: levels of government ----------

-- Parents first: DuckDB checks the foreign key row by row within one statement.
INSERT OR IGNORE INTO gov_unit VALUES
    ('at_general_government', 'Gesamtstaat',            'other',           'S13',   NULL),
    ('eu',                    'Europäische Union',      'eu',              NULL,    NULL);

INSERT OR IGNORE INTO gov_unit VALUES
    ('bund',                'Bund',                   'bund',            'S1311', 'at_general_government'),
    ('laender',               'Länder (ohne Wien)',      'land',            'S1312', 'at_general_government'),
    ('gemeinden',             'Gemeinden (ohne Wien)',   'gemeinde',        'S1313', 'at_general_government'),
    ('social_security',       'Sozialversicherung',     'social_security', 'S1314', 'at_general_government');

INSERT OR IGNORE INTO gov_unit VALUES
    ('wien_land',             'Wien als Land',          'land',            'S1312', 'laender'),
    ('wien_gemeinde',         'Wien als Gemeinde',      'gemeinde',        'S1313', 'gemeinden');
