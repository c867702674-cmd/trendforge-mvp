CREATE TABLE IF NOT EXISTS trend_expansion_v57 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  base_term TEXT,
  expanded_term TEXT,
  expansion_type TEXT,
  score REAL DEFAULT 0,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_trend_expansion_v57_base
ON trend_expansion_v57(base_term);
