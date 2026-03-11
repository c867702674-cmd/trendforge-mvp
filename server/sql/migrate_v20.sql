
CREATE TABLE IF NOT EXISTS ai_opportunity_board (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  term TEXT,
  opportunity_score REAL,
  niche_score REAL,
  profit_score REAL,
  final_score REAL,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_opportunity_board_trend
ON ai_opportunity_board(trend_id);
