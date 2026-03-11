CREATE TABLE IF NOT EXISTS mj_prompt_v97 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
trend_id INTEGER,
source_term TEXT,
product_type TEXT,
style_hint TEXT,
mj_prompt TEXT,
negative_prompt TEXT,
mockup_prompt TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
