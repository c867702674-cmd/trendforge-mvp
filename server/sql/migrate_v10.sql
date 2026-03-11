CREATE TABLE IF NOT EXISTS design_concepts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  concept TEXT NOT NULL,
  style TEXT,
  score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_design_concepts_trend ON design_concepts(trend_id);

CREATE TABLE IF NOT EXISTS sku_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  product_type TEXT NOT NULL,
  title_seed TEXT,
  tags_json TEXT,
  score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_sku_packs_trend ON sku_packs(trend_id);

CREATE TABLE IF NOT EXISTS listing_drafts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  trend_id INTEGER NOT NULL,
  concept_id INTEGER,
  sku_pack_id INTEGER,
  platform TEXT DEFAULT 'amazon',
  title TEXT,
  bullets_json TEXT,
  description TEXT,
  tags_json TEXT,
  score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_listing_drafts_trend ON listing_drafts(trend_id);
CREATE INDEX IF NOT EXISTS idx_listing_drafts_platform ON listing_drafts(platform);
