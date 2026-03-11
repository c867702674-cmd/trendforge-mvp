-- TrendForge V91 Push Center
CREATE TABLE IF NOT EXISTS push_channels_v91 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    channel_code TEXT UNIQUE,
    channel_name TEXT,
    is_enabled INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS push_queue_v91 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    trend_id INTEGER,
    source_term TEXT,
    action_level TEXT,
    product_type TEXT,
    target_channel TEXT,
    push_status TEXT,
    push_title TEXT,
    push_body TEXT,
    scheduled_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS push_dashboard_v91 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    queue_id INTEGER,
    target_channel TEXT,
    push_status TEXT,
    push_title TEXT,
    push_body TEXT,
    scheduled_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_push_queue_v91_status ON push_queue_v91(push_status);
CREATE INDEX IF NOT EXISTS idx_push_dashboard_v91_channel ON push_dashboard_v91(target_channel);
