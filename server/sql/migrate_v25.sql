
CREATE TABLE IF NOT EXISTS pod_niche_profits (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 niche_score REAL,
 profit_score REAL,
 demand_score REAL,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_pod_niche_term
ON pod_niche_profits(term);
