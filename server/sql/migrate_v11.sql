CREATE TABLE IF NOT EXISTS listing_quality_logs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  listing_id INTEGER NOT NULL,
  score REAL DEFAULT 0,
  quality_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_listing_quality_logs_listing
ON listing_quality_logs(listing_id);
ALTER TABLE listing_drafts ADD COLUMN rank_score REAL DEFAULT 0;
ALTER TABLE listing_drafts ADD COLUMN quality_json TEXT;
