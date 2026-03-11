CREATE TABLE IF NOT EXISTS niche_signals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  niche_term TEXT,
  signal_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_niche_signals_trend ON niche_signals(trend_id);

CREATE TABLE IF NOT EXISTS market_gaps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  gap_type TEXT,
  gap_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_market_gaps_trend ON market_gaps(trend_id);

CREATE TABLE IF NOT EXISTS execution_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  listing_id INTEGER,
  pack_json TEXT,
  score REAL DEFAULT 0,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_execution_packs_trend ON execution_packs(trend_id);
