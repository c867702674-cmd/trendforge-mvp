-- TrendForge V64 Command Center Engine
CREATE TABLE IF NOT EXISTS command_center_v64 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    schedule_bucket TEXT,
    publish_status TEXT,
    board_column TEXT,
    ops_stage TEXT,
    dashboard_score REAL DEFAULT 0,
    commander_lane TEXT,
    commander_action TEXT,
    command_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_command_v64_lane
ON command_center_v64(commander_lane);

CREATE INDEX IF NOT EXISTS idx_command_v64_product
ON command_center_v64(product_type);

CREATE INDEX IF NOT EXISTS idx_command_v64_score
ON command_center_v64(command_score DESC);
