-- TrendForge V94 Feishu Webhook Engine
CREATE TABLE IF NOT EXISTS feishu_push_logs_v94 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_job_id INTEGER,
    target_channel TEXT,
    webhook_url TEXT,
    push_status TEXT,
    response_text TEXT,
    pushed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feishu_push_dashboard_v94 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_job_id INTEGER,
    target_channel TEXT,
    push_status TEXT,
    response_text TEXT,
    pushed_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feishu_push_logs_v94_status ON feishu_push_logs_v94(push_status);
