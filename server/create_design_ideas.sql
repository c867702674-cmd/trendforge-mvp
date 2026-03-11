-- TrendForge: create design_ideas table for Trend Expansion Engine
-- Compatible with TrendForge V6 (SQLite)

CREATE TABLE IF NOT EXISTS design_ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  idea TEXT NOT NULL,
  category TEXT DEFAULT 'POD',
  score REAL DEFAULT 0,
  meta_json TEXT,
  created_at TEXT NOT NULL
);

-- Prevent duplicates per trend
CREATE UNIQUE INDEX IF NOT EXISTS ux_design_ideas_trend_idea
ON design_ideas(trend_id, idea);

CREATE INDEX IF NOT EXISTS idx_design_ideas_trend
ON design_ideas(trend_id);

CREATE INDEX IF NOT EXISTS idx_design_ideas_score
ON design_ideas(score);
