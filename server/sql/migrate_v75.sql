-- TrendForge V75 Dispatch Center Engine
CREATE TABLE IF NOT EXISTS dispatch_center_v75 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    release_routing_id INTEGER,
    allocation_board_id INTEGER,
    portfolio_matrix_id INTEGER,
    executive_grid_id INTEGER,
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
    routing_lane TEXT,
    routing_score REAL DEFAULT 0,
    dispatch_lane TEXT,
    dispatch_action TEXT,
    dispatch_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_dispatch_v75_lane
ON dispatch_center_v75(dispatch_lane);

CREATE INDEX IF NOT EXISTS idx_dispatch_v75_product
ON dispatch_center_v75(product_type);

CREATE INDEX IF NOT EXISTS idx_dispatch_v75_score
ON dispatch_center_v75(dispatch_score DESC);
