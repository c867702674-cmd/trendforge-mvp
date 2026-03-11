-- TrendForge V61 Launch Queue Engine
CREATE TABLE IF NOT EXISTS launch_queue_v61 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    execution_pack_id INTEGER,
    listing_id INTEGER,
    source_term TEXT,
    safe_term TEXT,
    risk_level TEXT,
    product_type TEXT,
    title_en TEXT,
    sku_code TEXT,
    pack_score REAL DEFAULT 0,
    priority_tier TEXT,
    schedule_bucket TEXT,
    publish_status TEXT DEFAULT 'READY',
    checklist_text TEXT,
    operator_note TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_launch_v61_priority
ON launch_queue_v61(priority_tier);

CREATE INDEX IF NOT EXISTS idx_launch_v61_bucket
ON launch_queue_v61(schedule_bucket);

CREATE INDEX IF NOT EXISTS idx_launch_v61_status
ON launch_queue_v61(publish_status);

CREATE INDEX IF NOT EXISTS idx_launch_v61_product
ON launch_queue_v61(product_type);
