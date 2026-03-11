CREATE TABLE IF NOT EXISTS pod_keywords (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  date TEXT,
  country TEXT,
  source TEXT,
  keyword TEXT,
  score REAL DEFAULT 0,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_pod_keywords_date ON pod_keywords(date);
CREATE INDEX IF NOT EXISTS idx_pod_keywords_source ON pod_keywords(source);
CREATE INDEX IF NOT EXISTS idx_pod_keywords_keyword ON pod_keywords(keyword);

CREATE TABLE IF NOT EXISTS trend_source_health (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  source TEXT NOT NULL,
  run_at TEXT NOT NULL,
  ok INTEGER NOT NULL DEFAULT 0,
  inserted_count INTEGER NOT NULL DEFAULT 0,
  error TEXT
);
CREATE INDEX IF NOT EXISTS idx_trend_source_health_source ON trend_source_health(source, run_at);
