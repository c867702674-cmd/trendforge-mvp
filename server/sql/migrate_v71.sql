-- TrendForge V71 Executive Grid Engine
CREATE TABLE IF NOT EXISTS executive_grid_v71 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    strategic_hub_id INTEGER,
    operations_hq_id INTEGER,
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
    hub_lane TEXT,
    hub_score REAL DEFAULT 0,
    exec_lane TEXT,
    exec_action TEXT,
    exec_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_exec_v71_lane
ON executive_grid_v71(exec_lane);

CREATE INDEX IF NOT EXISTS idx_exec_v71_product
ON executive_grid_v71(product_type);

CREATE INDEX IF NOT EXISTS idx_exec_v71_score
ON executive_grid_v71(exec_score DESC);
