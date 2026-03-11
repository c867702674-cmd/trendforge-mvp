
CREATE TABLE IF NOT EXISTS seller_dashboard_snapshots (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 snapshot_name TEXT,
 payload_json TEXT,
 created_at TEXT
);
