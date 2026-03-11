CREATE TABLE IF NOT EXISTS mockup_pack_v98 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
prompt_id INTEGER,
source_term TEXT,
product_type TEXT,
hero_mockup TEXT,
scene_mockup TEXT,
white_bg_mockup TEXT,
detail_mockup TEXT,
mockup_pack_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
