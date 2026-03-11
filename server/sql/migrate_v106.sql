CREATE TABLE IF NOT EXISTS home_portal_v106 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
block_name TEXT,
block_title TEXT,
block_value TEXT,
block_note TEXT,
status TEXT,
sort_order INTEGER,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
