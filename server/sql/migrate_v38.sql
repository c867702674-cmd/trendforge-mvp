CREATE TABLE IF NOT EXISTS audience_routes (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 route_name TEXT,
 audience TEXT,
 priority_score REAL,
 title TEXT,
 body_json TEXT,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_audience_routes_term
ON audience_routes(term);
