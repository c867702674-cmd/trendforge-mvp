-- TrendForge V85 Commercial Launch Console
CREATE TABLE IF NOT EXISTS commercial_launch_v85 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    launch_checklist_id INTEGER,
    commercial_golive_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    launch_lane TEXT,
    owner_role TEXT,
    publish_status TEXT,
    blocker_text TEXT,
    next_action TEXT,
    launch_pack_text TEXT,
    launch_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_commercial_launch_v85_lane ON commercial_launch_v85(launch_lane);
CREATE INDEX IF NOT EXISTS idx_commercial_launch_v85_score ON commercial_launch_v85(launch_score DESC);
