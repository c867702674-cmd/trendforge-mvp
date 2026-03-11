
CREATE TABLE IF NOT EXISTS auto_trend_discoveries (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 discovery_score REAL,
 signal_sources INTEGER,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_auto_trend_term
ON auto_trend_discoveries(term);
