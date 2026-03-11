CREATE TABLE IF NOT EXISTS seller_flow_snapshots (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 flow_name TEXT,
 payload_json TEXT,
 created_at TEXT
);
