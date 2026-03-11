CREATE TABLE IF NOT EXISTS dashboard_views (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  view_name TEXT NOT NULL,
  payload_json TEXT,
  created_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_dashboard_views_name ON dashboard_views(view_name);
