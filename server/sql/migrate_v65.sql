-- TrendForge V65 Batch Studio Engine
CREATE TABLE IF NOT EXISTS batch_studio_v65 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_center_id INTEGER,
    ops_dashboard_id INTEGER,
    publish_board_id INTEGER,
    launch_queue_id INTEGER,
    execution_pack_id INTEGER,
    listing_id INTEGER,
    source_term TEXT,
    safe_term TEXT,
    risk_level TEXT,
    product_type TEXT,
    title_en TEXT,
    sku_code TEXT,
    priority_tier TEXT,
    commander_lane TEXT,
    command_score REAL DEFAULT 0,
    batch_group TEXT,
    batch_action TEXT,
    batch_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_batch_v65_group
ON batch_studio_v65(batch_group);

CREATE INDEX IF NOT EXISTS idx_batch_v65_product
ON batch_studio_v65(product_type);

CREATE INDEX IF NOT EXISTS idx_batch_v65_score
ON batch_studio_v65(batch_score DESC);
