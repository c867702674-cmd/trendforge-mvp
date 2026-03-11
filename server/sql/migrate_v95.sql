-- TrendForge V95 Feishu Card Studio
CREATE TABLE IF NOT EXISTS feishu_card_jobs_v95 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trend_id INTEGER,
    source_term TEXT,
    action_level TEXT,
    product_type TEXT,
    target_channel TEXT,
    card_title TEXT,
    card_summary TEXT,
    card_json TEXT,
    send_status TEXT,
    response_text TEXT,
    sent_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS feishu_card_dashboard_v95 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_id INTEGER,
    target_channel TEXT,
    card_title TEXT,
    send_status TEXT,
    response_text TEXT,
    sent_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_feishu_card_jobs_v95_status ON feishu_card_jobs_v95(send_status);
