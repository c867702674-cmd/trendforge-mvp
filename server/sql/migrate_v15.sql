CREATE TABLE IF NOT EXISTS trend_source_stats (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  run_at TEXT NOT NULL,
  ok INTEGER NOT NULL DEFAULT 0,
  inserted_count INTEGER NOT NULL DEFAULT 0,
  blocked_count INTEGER NOT NULL DEFAULT 0,
  error TEXT
);
CREATE INDEX IF NOT EXISTS idx_trend_source_stats_source
ON trend_source_stats(source, run_at);
ALTER TABLE trends ADD COLUMN pod_relevance_score REAL DEFAULT 0;
