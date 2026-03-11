-- TrendForge V66 Mission Planner Engine
CREATE TABLE IF NOT EXISTS mission_planner_v66 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    batch_group TEXT,
    batch_score REAL DEFAULT 0,
    mission_lane TEXT,
    mission_action TEXT,
    mission_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_mission_v66_lane
ON mission_planner_v66(mission_lane);

CREATE INDEX IF NOT EXISTS idx_mission_v66_product
ON mission_planner_v66(product_type);

CREATE INDEX IF NOT EXISTS idx_mission_v66_score
ON mission_planner_v66(mission_score DESC);
