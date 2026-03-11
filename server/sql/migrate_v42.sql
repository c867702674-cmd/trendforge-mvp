
CREATE TABLE IF NOT EXISTS push_schedule_logs (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 schedule_name TEXT,
 triggered INTEGER,
 result TEXT,
 created_at TEXT
);
