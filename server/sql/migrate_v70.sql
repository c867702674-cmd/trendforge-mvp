-- TrendForge V70 Strategic Hub Engine
CREATE TABLE IF NOT EXISTS strategic_hub_v70 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    hq_lane TEXT,
    hq_score REAL DEFAULT 0,
    hub_lane TEXT,
    hub_action TEXT,
    hub_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_hub_v70_lane
ON strategic_hub_v70(hub_lane);

CREATE INDEX IF NOT EXISTS idx_hub_v70_product
ON strategic_hub_v70(product_type);

CREATE INDEX IF NOT EXISTS idx_hub_v70_score
ON strategic_hub_v70(hub_score DESC);
