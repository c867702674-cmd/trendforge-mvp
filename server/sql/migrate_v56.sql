
CREATE TABLE IF NOT EXISTS pod_sku_packs_v56 (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  term TEXT,
  sku_type TEXT,
  sku_title TEXT,
  mj_prompt TEXT,
  listing_title TEXT,
  tags_json TEXT,
  created_at TEXT
);
