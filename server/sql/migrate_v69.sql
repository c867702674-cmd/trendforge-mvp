-- TrendForge V69 Operations HQ Engine
CREATE TABLE IF NOT EXISTS operations_hq_v69 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    war_room_id INTEGER,
    control_tower_id INTEGER,
    mission_planner_id INTEGER,
    batch_studio_id INTEGER,
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
    war_lane TEXT,
    war_score REAL DEFAULT 0,
    hq_lane TEXT,
    hq_action TEXT,
    hq_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hq_v69_lane
ON operations_hq_v69(hq_lane);

CREATE INDEX IF NOT EXISTS idx_hq_v69_product
ON operations_hq_v69(product_type);

CREATE INDEX IF NOT EXISTS idx_hq_v69_score
ON operations_hq_v69(hq_score DESC);
