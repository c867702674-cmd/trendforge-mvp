CREATE TABLE IF NOT EXISTS commercial_dashboard_v105 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
section_name TEXT,
section_value TEXT,
section_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
