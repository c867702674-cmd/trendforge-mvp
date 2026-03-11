CREATE TABLE IF NOT EXISTS tiktok_trend_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  trend_type TEXT,
  term TEXT NOT NULL,
  signal_score REAL DEFAULT 0,
  intent_label TEXT,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tiktok_trend_signals_term
ON tiktok_trend_signals(term);

CREATE TABLE IF NOT EXISTS tiktok_semantic_links (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source_term TEXT NOT NULL,
  bridge_term TEXT NOT NULL,
  bridge_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_tiktok_semantic_links_source
ON tiktok_semantic_links(source_term);
