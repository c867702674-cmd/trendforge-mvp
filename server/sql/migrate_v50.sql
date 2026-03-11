CREATE TABLE IF NOT EXISTS ai_trend_scorecards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  term TEXT,
  trend_power_score REAL DEFAULT 0,
  profit_score REAL DEFAULT 0,
  competition_score REAL DEFAULT 0,
  design_difficulty REAL DEFAULT 0,
  viral_probability REAL DEFAULT 0,
  decision_level TEXT,
  design_direction TEXT,
  product_ideas_json TEXT,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_trend_scorecards_term
ON ai_trend_scorecards(term);
