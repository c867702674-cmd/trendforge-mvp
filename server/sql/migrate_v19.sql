CREATE TABLE IF NOT EXISTS ai_trend_brain (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  cluster_label TEXT,
  brain_score REAL DEFAULT 0,
  opportunity_score REAL DEFAULT 0,
  risk_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_ai_trend_brain_trend ON ai_trend_brain(trend_id);

CREATE TABLE IF NOT EXISTS niche_opportunities (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  niche_label TEXT,
  niche_score REAL DEFAULT 0,
  competition_score REAL DEFAULT 0,
  demand_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_niche_opportunities_trend ON niche_opportunities(trend_id);

CREATE TABLE IF NOT EXISTS pod_image_prompts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  listing_id INTEGER,
  prompt_type TEXT,
  prompt_text TEXT,
  prompt_score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_pod_image_prompts_trend ON pod_image_prompts(trend_id);
