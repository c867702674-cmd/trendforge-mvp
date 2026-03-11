
CREATE TABLE IF NOT EXISTS listing_auto_drafts (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 listing_title TEXT,
 bullet_points_json TEXT,
 description TEXT,
 seo_tags_json TEXT,
 image_prompt TEXT,
 draft_score REAL DEFAULT 0,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_listing_auto_term
ON listing_auto_drafts(term);
