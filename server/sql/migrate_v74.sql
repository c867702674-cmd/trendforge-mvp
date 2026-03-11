-- TrendForge V74 Release Routing Engine
CREATE TABLE IF NOT EXISTS release_routing_v74 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    allocation_lane TEXT,
    allocation_score REAL DEFAULT 0,
    routing_lane TEXT,
    routing_action TEXT,
    routing_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_routing_v74_lane
ON release_routing_v74(routing_lane);

CREATE INDEX IF NOT EXISTS idx_routing_v74_product
ON release_routing_v74(product_type);

CREATE INDEX IF NOT EXISTS idx_routing_v74_score
ON release_routing_v74(routing_score DESC);
