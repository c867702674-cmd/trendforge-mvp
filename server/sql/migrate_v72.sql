-- TrendForge V72 Portfolio Matrix Engine
CREATE TABLE IF NOT EXISTS portfolio_matrix_v72 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    exec_lane TEXT,
    exec_score REAL DEFAULT 0,
    matrix_lane TEXT,
    matrix_action TEXT,
    matrix_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_matrix_v72_lane
ON portfolio_matrix_v72(matrix_lane);

CREATE INDEX IF NOT EXISTS idx_matrix_v72_product
ON portfolio_matrix_v72(product_type);

CREATE INDEX IF NOT EXISTS idx_matrix_v72_score
ON portfolio_matrix_v72(matrix_score DESC);
