-- TrendForge V83 Commercial Go-Live Center
CREATE TABLE IF NOT EXISTS commercial_golive_v83 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    launch_readiness_id INTEGER,
    saas_dashboard_id INTEGER,
    listing_ai_id INTEGER,
    mj_prompt_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    golive_lane TEXT,
    golive_note TEXT,
    operator_action TEXT,
    checklist_text TEXT,
    golive_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_commercial_golive_v83_lane ON commercial_golive_v83(golive_lane);
CREATE INDEX IF NOT EXISTS idx_commercial_golive_v83_score ON commercial_golive_v83(golive_score DESC);
