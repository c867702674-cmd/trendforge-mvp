CREATE TABLE IF NOT EXISTS ai_listing_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  term TEXT,
  platform TEXT,
  title TEXT,
  bullet_1 TEXT,
  bullet_2 TEXT,
  bullet_3 TEXT,
  bullet_4 TEXT,
  bullet_5 TEXT,
  description TEXT,
  tags_json TEXT,
  design_prompt TEXT,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_ai_listing_drafts_term
ON ai_listing_drafts(term);
