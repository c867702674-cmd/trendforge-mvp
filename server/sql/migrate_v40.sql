CREATE TABLE IF NOT EXISTS feishu_push_results (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 audience TEXT,
 title TEXT,
 ok INTEGER,
 dry_run INTEGER,
 http_status INTEGER,
 response_text TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_feishu_push_results_term
ON feishu_push_results(term);
