CREATE TABLE IF NOT EXISTS creative_pack_v100 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
brief_id INTEGER,
source_term TEXT,
product_type TEXT,
title_idea TEXT,
tagline TEXT,
visual_direction TEXT,
prompt_pack TEXT,
mockup_pack TEXT,
production_checklist TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
