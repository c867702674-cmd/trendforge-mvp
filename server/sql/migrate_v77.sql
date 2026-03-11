-- TrendForge V77 Launch Control Engine
CREATE TABLE IF NOT EXISTS launch_control_v77 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    launch_orchestrator_id INTEGER,
    dispatch_center_id INTEGER,
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
    orchestrator_lane TEXT,
    orchestrator_score REAL DEFAULT 0,
    control_lane TEXT,
    control_action TEXT,
    control_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_control_v77_lane
ON launch_control_v77(control_lane);

CREATE INDEX IF NOT EXISTS idx_control_v77_product
ON launch_control_v77(product_type);

CREATE INDEX IF NOT EXISTS idx_control_v77_score
ON launch_control_v77(control_score DESC);
