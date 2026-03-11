-- TrendForge V82 Launch Readiness Center
CREATE TABLE IF NOT EXISTS launch_readiness_v82 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    saas_dashboard_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    readiness_lane TEXT,
    readiness_note TEXT,
    checklist_text TEXT,
    readiness_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_launch_readiness_v82_lane ON launch_readiness_v82(readiness_lane);
CREATE INDEX IF NOT EXISTS idx_launch_readiness_v82_score ON launch_readiness_v82(readiness_score DESC);
