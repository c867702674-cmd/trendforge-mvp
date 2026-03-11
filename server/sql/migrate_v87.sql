-- TrendForge V87 Command Center
CREATE TABLE IF NOT EXISTS command_center_v87 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    launch_ops_id INTEGER,
    commercial_launch_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    center_lane TEXT,
    center_module TEXT,
    owner_role TEXT,
    center_status TEXT,
    blocker_text TEXT,
    next_action TEXT,
    summary_text TEXT,
    center_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_command_center_v87_lane ON command_center_v87(center_lane);
CREATE INDEX IF NOT EXISTS idx_command_center_v87_score ON command_center_v87(center_score DESC);
