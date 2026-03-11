-- TrendForge V93 Execution Engine
CREATE TABLE IF NOT EXISTS execution_jobs_v93 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    automation_job_id INTEGER,
    rule_code TEXT,
    target_channel TEXT,
    execution_status TEXT,
    executed_at TEXT,
    execution_log TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS execution_dashboard_v93 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    rule_code TEXT,
    target_channel TEXT,
    execution_status TEXT,
    executed_at TEXT,
    execution_log TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_execution_jobs_status_v93 ON execution_jobs_v93(execution_status);
