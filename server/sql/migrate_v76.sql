-- TrendForge V76 Launch Orchestrator Engine
CREATE TABLE IF NOT EXISTS launch_orchestrator_v76 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    dispatch_lane TEXT,
    dispatch_score REAL DEFAULT 0,
    orchestrator_lane TEXT,
    orchestrator_action TEXT,
    orchestrator_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_orchestrator_v76_lane
ON launch_orchestrator_v76(orchestrator_lane);

CREATE INDEX IF NOT EXISTS idx_orchestrator_v76_product
ON launch_orchestrator_v76(product_type);

CREATE INDEX IF NOT EXISTS idx_orchestrator_v76_score
ON launch_orchestrator_v76(orchestrator_score DESC);
