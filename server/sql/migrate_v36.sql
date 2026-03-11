CREATE TABLE IF NOT EXISTS execution_pack_distributions (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 pack_title TEXT,
 pack_score REAL,
 task_list_json TEXT,
 listing_title TEXT,
 image_prompt TEXT,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_execution_pack_dist_term
ON execution_pack_distributions(term);
