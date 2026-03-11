CREATE TABLE IF NOT EXISTS homepage_v107 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
section_key TEXT,
section_title TEXT,
section_value TEXT,
section_desc TEXT,
status TEXT,
sort_order INTEGER,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
