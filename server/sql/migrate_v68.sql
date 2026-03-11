-- TrendForge V68 War Room Engine
CREATE TABLE IF NOT EXISTS war_room_v68 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    tower_lane TEXT,
    tower_score REAL DEFAULT 0,
    war_lane TEXT,
    war_action TEXT,
    war_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_war_v68_lane
ON war_room_v68(war_lane);

CREATE INDEX IF NOT EXISTS idx_war_v68_product
ON war_room_v68(product_type);

CREATE INDEX IF NOT EXISTS idx_war_v68_score
ON war_room_v68(war_score DESC);
