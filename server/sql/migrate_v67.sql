-- TrendForge V67 Control Tower Engine
CREATE TABLE IF NOT EXISTS control_tower_v67 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    mission_lane TEXT,
    mission_score REAL DEFAULT 0,
    tower_lane TEXT,
    tower_action TEXT,
    tower_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_tower_v67_lane
ON control_tower_v67(tower_lane);

CREATE INDEX IF NOT EXISTS idx_tower_v67_product
ON control_tower_v67(product_type);

CREATE INDEX IF NOT EXISTS idx_tower_v67_score
ON control_tower_v67(tower_score DESC);
