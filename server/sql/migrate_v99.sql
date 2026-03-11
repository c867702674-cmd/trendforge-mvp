CREATE TABLE IF NOT EXISTS image_brief_v99 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
mockup_id INTEGER,
source_term TEXT,
product_type TEXT,
hero_brief TEXT,
color_brief TEXT,
composition_brief TEXT,
copy_brief TEXT,
production_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
