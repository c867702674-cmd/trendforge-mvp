-- TrendForge V84 Launch Checklist Hub
CREATE TABLE IF NOT EXISTS launch_checklist_v84 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    commercial_golive_id INTEGER,
    launch_readiness_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    checklist_lane TEXT,
    checklist_owner TEXT,
    checklist_status TEXT,
    must_do_text TEXT,
    launch_blocker TEXT,
    next_action TEXT,
    checklist_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_launch_checklist_v84_lane ON launch_checklist_v84(checklist_lane);
CREATE INDEX IF NOT EXISTS idx_launch_checklist_v84_score ON launch_checklist_v84(checklist_score DESC);
