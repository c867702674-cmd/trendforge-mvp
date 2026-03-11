-- TrendForge V92 Automation Hub
CREATE TABLE IF NOT EXISTS automation_rules_v92 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    rule_code TEXT UNIQUE,
    rule_name TEXT,
    target_channel TEXT,
    trigger_action_level TEXT,
    is_enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automation_jobs_v92 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    push_dashboard_id INTEGER,
    rule_code TEXT,
    target_channel TEXT,
    job_status TEXT,
    execute_at TEXT,
    result_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS automation_dashboard_v92 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    rule_code TEXT,
    target_channel TEXT,
    job_status TEXT,
    execute_at TEXT,
    result_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_automation_jobs_v92_status ON automation_jobs_v92(job_status);
CREATE INDEX IF NOT EXISTS idx_automation_dashboard_v92_channel ON automation_dashboard_v92(target_channel);
