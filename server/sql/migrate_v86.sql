-- TrendForge V86 Launch Ops Board
CREATE TABLE IF NOT EXISTS launch_ops_v86 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commercial_launch_id INTEGER,
    launch_checklist_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    ops_lane TEXT,
    owner_role TEXT,
    ops_status TEXT,
    blocker_text TEXT,
    next_action TEXT,
    publish_note TEXT,
    ops_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_launch_ops_v86_lane ON launch_ops_v86(ops_lane);
CREATE INDEX IF NOT EXISTS idx_launch_ops_v86_score ON launch_ops_v86(ops_score DESC);
