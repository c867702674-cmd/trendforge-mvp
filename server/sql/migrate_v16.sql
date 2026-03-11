CREATE TABLE IF NOT EXISTS seller_accounts (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  email TEXT UNIQUE,
  name TEXT,
  tier TEXT DEFAULT 'trial',
  created_at TEXT
);

CREATE TABLE IF NOT EXISTS seller_projects (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER NOT NULL,
  project_name TEXT NOT NULL,
  market TEXT DEFAULT 'US',
  platform TEXT DEFAULT 'amazon',
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_seller_projects_seller ON seller_projects(seller_id);

CREATE TABLE IF NOT EXISTS seller_saved_trends (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER NOT NULL,
  trend_id INTEGER NOT NULL,
  note TEXT,
  created_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_seller_saved_trends ON seller_saved_trends(seller_id, trend_id);

CREATE TABLE IF NOT EXISTS seller_execution_packs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  seller_id INTEGER NOT NULL,
  execution_pack_id INTEGER NOT NULL,
  status TEXT DEFAULT 'saved',
  created_at TEXT
);
CREATE UNIQUE INDEX IF NOT EXISTS ux_seller_execution_packs ON seller_execution_packs(seller_id, execution_pack_id);

ALTER TABLE listing_drafts ADD COLUMN amazon_title TEXT;
ALTER TABLE listing_drafts ADD COLUMN amazon_bullets_json TEXT;
ALTER TABLE listing_drafts ADD COLUMN amazon_description TEXT;
ALTER TABLE listing_drafts ADD COLUMN amazon_search_terms TEXT;
