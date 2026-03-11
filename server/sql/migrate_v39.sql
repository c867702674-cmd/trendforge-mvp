CREATE TABLE IF NOT EXISTS push_dispatch_logs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 route_name TEXT,
 audience TEXT,
 title TEXT,
 dispatched INTEGER,
 created_at TEXT
);
