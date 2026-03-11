CREATE TABLE IF NOT EXISTS seller_alerts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 alert_level TEXT,
 alert_title TEXT,
 alert_text TEXT,
 alert_score REAL,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_seller_alerts_term
ON seller_alerts(term);
