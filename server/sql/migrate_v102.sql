CREATE TABLE IF NOT EXISTS publish_pack_v102 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
listing_id INTEGER,
source_term TEXT,
product_type TEXT,
publish_title TEXT,
publish_subtitle TEXT,
publish_checklist TEXT,
marketplace_note TEXT,
final_publish_pack TEXT,
operator_action TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
