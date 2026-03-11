CREATE TABLE IF NOT EXISTS push_control_snapshots (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 snapshot_name TEXT,
 payload_json TEXT,
 created_at TEXT
);
