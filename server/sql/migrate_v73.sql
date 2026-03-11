-- TrendForge V73 Allocation Engine
CREATE TABLE IF NOT EXISTS allocation_board_v73 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    matrix_lane TEXT,
    matrix_score REAL DEFAULT 0,
    allocation_lane TEXT,
    allocation_action TEXT,
    allocation_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_allocation_v73_lane
ON allocation_board_v73(allocation_lane);

CREATE INDEX IF NOT EXISTS idx_allocation_v73_product
ON allocation_board_v73(product_type);

CREATE INDEX IF NOT EXISTS idx_allocation_v73_score
ON allocation_board_v73(allocation_score DESC);
