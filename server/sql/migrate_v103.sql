CREATE TABLE IF NOT EXISTS release_queue_v103 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
publish_id INTEGER,
source_term TEXT,
product_type TEXT,
queue_name TEXT,
priority TEXT,
risk_level TEXT,
release_note TEXT,
next_step TEXT,
operator_owner TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
