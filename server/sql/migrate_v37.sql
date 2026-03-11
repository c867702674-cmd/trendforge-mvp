CREATE TABLE IF NOT EXISTS push_ready_payloads (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 payload_type TEXT,
 priority_score REAL,
 audience TEXT,
 title TEXT,
 body_json TEXT,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_push_ready_term
ON push_ready_payloads(term);
