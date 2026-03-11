-- TrendForge V7 DB migration (SQLite)
-- Adds/ensures tables needed for:
-- 1) design_ideas (trend expansion output)
-- 2) design_prompts (MJ prompt generator output)

-- ---------- design_ideas ----------
CREATE TABLE IF NOT EXISTS design_ideas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  idea TEXT NOT NULL,
  category TEXT DEFAULT 'POD',
  score REAL DEFAULT 0,
  meta_json TEXT,
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_design_ideas_trend_idea
ON design_ideas(trend_id, idea);

CREATE INDEX IF NOT EXISTS idx_design_ideas_trend
ON design_ideas(trend_id);

CREATE INDEX IF NOT EXISTS idx_design_ideas_score
ON design_ideas(score);

-- ---------- design_prompts ----------
CREATE TABLE IF NOT EXISTS design_prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  idea_id INTEGER NOT NULL,
  prompt TEXT NOT NULL,
  model TEXT DEFAULT 'midjourney',
  style TEXT,
  score REAL DEFAULT 0,
  meta_json TEXT,
  created_at TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS ux_design_prompts_idea_model
ON design_prompts(idea_id, model);

CREATE INDEX IF NOT EXISTS idx_design_prompts_idea
ON design_prompts(idea_id);

CREATE INDEX IF NOT EXISTS idx_design_prompts_score
ON design_prompts(score);
