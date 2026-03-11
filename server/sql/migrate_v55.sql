CREATE TABLE IF NOT EXISTS mj_prompt_drafts_v55 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  term TEXT,
  platform TEXT,
  style_name TEXT,
  subject_line TEXT,
  mj_prompt TEXT,
  sdxl_prompt TEXT,
  negative_prompt TEXT,
  aspect_ratio TEXT,
  sku_hint TEXT,
  payload_json TEXT,
  created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_mj_prompt_drafts_v55_term
ON mj_prompt_drafts_v55(term);
