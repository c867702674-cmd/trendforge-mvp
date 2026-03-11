CREATE TABLE IF NOT EXISTS ai_trend_rankings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  term TEXT NOT NULL,
  brain_score REAL DEFAULT 0,
  niche_score REAL DEFAULT 0,
  board_score REAL DEFAULT 0,
  source_count REAL DEFAULT 0,
  rank_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_trend_rankings_trend
ON ai_trend_rankings(trend_id);
