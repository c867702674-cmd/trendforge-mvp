CREATE TABLE IF NOT EXISTS listing_pack_v101 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
creative_id INTEGER,
source_term TEXT,
product_type TEXT,
listing_title TEXT,
listing_bullets TEXT,
listing_tags TEXT,
listing_description TEXT,
sku TEXT,
listing_note TEXT,
status TEXT,
created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
