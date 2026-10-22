
CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS core;
CREATE SCHEMA IF NOT EXISTS audit;
CREATE SCHEMA IF NOT EXISTS analytics;

-- =====================================================
-- CORE: datos estructurados y relaciones
-- =====================================================

CREATE TABLE core.district (
    district_id              INT PRIMARY KEY, -- A1
    district_name            TEXT NOT NULL,  -- A2
    region                   TEXT NOT NULL,  -- A3
    inhabitants              INT,             -- A4
    municipalities_lt_499    INT,             -- A5
    municipalities_500_1999  INT,             -- A6
    municipalities_2000_9999 INT,             -- A7
    municipalities_gt_10000  INT,             -- A8
    n_cities                 INT,             -- A9
    urban_ratio              NUMERIC(5,2),    -- A10
    avg_salary               INT,             -- A11
    unemployment_95          NUMERIC(5,2),    -- A12
    unemployment_96          NUMERIC(5,2),    -- A13
    entrepreneurs_per_1000   INT,             -- A14
    crimes_95                INT,             -- A15
    crimes_96                INT              -- A16
);

CREATE TABLE core.client (
    client_id    INT PRIMARY KEY,
    birth_number TEXT NOT NULL,
    birth_date   DATE, -- Opcional hasta validar transformación
    gender       CHAR(1)
        CHECK (gender IN ('M', 'F')),
    district_id  INT NOT NULL
        REFERENCES core.district(district_id)
);

CREATE TABLE core.account (
    account_id   INT PRIMARY KEY,
    district_id  INT NOT NULL
        REFERENCES core.district(district_id),
    frequency    TEXT NOT NULL,
    created_date DATE NOT NULL
);

CREATE TABLE core.disp (
    disp_id      INT PRIMARY KEY,
    client_id    INT NOT NULL
        REFERENCES core.client(client_id),
    account_id   INT NOT NULL
        REFERENCES core.account(account_id),
    disp_type    TEXT NOT NULL
        CHECK (disp_type IN ('OWNER', 'DISPONENT'))
);

CREATE TABLE core.card (
    card_id      INT PRIMARY KEY,
    disp_id      INT NOT NULL
        REFERENCES core.disp(disp_id),
    card_type    TEXT NOT NULL,
    issued_date  DATE NOT NULL
);

CREATE TABLE core.loan (
    loan_id      INT PRIMARY KEY,
    account_id   INT NOT NULL
        REFERENCES core.account(account_id),
    loan_date    DATE NOT NULL,
    amount       NUMERIC(14,2) NOT NULL
        CHECK (amount > 0),
    duration     INT NOT NULL
        CHECK (duration > 0),
    payments     NUMERIC(14,2) NOT NULL
        CHECK (payments > 0),
    status       CHAR(1) NOT NULL
        CHECK (status IN ('A', 'B', 'C', 'D'))
);

CREATE TABLE core.permanent_order (
    order_id     INT PRIMARY KEY,
    account_id   INT NOT NULL
        REFERENCES core.account(account_id),
    bank_to      TEXT NOT NULL,
    account_to   TEXT NOT NULL,
    amount       NUMERIC(14,2) NOT NULL,
    k_symbol     TEXT
);

CREATE TABLE core.trans (
    trans_id     BIGINT PRIMARY KEY,
    account_id   INT NOT NULL
        REFERENCES core.account(account_id),
    trans_date   DATE NOT NULL,
    trans_type   TEXT NOT NULL,
    operation    TEXT,
    amount       NUMERIC(14,2) NOT NULL,
    balance      NUMERIC(14,2) NOT NULL,
    k_symbol     TEXT,
    bank         TEXT,
    account      TEXT
);

-- Índices para consultas frecuentes
CREATE INDEX idx_trans_account_date
    ON core.trans (account_id, trans_date);

CREATE INDEX idx_loan_account
    ON core.loan (account_id);

CREATE INDEX idx_disp_account
    ON core.disp (account_id);

-- =====================================================
-- AUDIT: seguimiento de ejecuciones y validaciones
-- =====================================================

CREATE TABLE audit.etl_run (
    run_id        SERIAL PRIMARY KEY,
    pipeline_name TEXT NOT NULL,
    started_at    TIMESTAMP NOT NULL DEFAULT now(),
    finished_at   TIMESTAMP,
    status        TEXT NOT NULL DEFAULT 'RUNNING'
        CHECK (status IN ('RUNNING', 'SUCCESS', 'FAILED'))
);

CREATE TABLE audit.validation_result (
    id           SERIAL PRIMARY KEY,
    run_id       INT REFERENCES audit.etl_run(run_id),
    table_name   TEXT NOT NULL,
    rule_name    TEXT NOT NULL,
    passed       BOOLEAN NOT NULL,
    rows_checked BIGINT,
    rows_failed  BIGINT,
    details      TEXT,
    checked_at   TIMESTAMP NOT NULL DEFAULT now()
);
