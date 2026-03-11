
CREATE TABLE IF NOT EXISTS seller_opportunity_feed (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 opportunity_score REAL,
 source TEXT,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_seller_opportunity_term
ON seller_opportunity_feed(term);
