CREATE TABLE IF NOT EXISTS discovery_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  term TEXT NOT NULL,
  signal_type TEXT,
  signal_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_discovery_signals_source_term
ON discovery_signals(source, term);

CREATE TABLE IF NOT EXISTS semantic_trend_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  base_term TEXT NOT NULL,
  expanded_term TEXT NOT NULL,
  link_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_semantic_trend_links_trend
ON semantic_trend_links(trend_id);
