-- TrendForge V80 Unified SaaS Dashboard
CREATE TABLE IF NOT EXISTS saas_dashboard_v80 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_ai_id INTEGER,
    release_command_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    tags_text TEXT,
    description_text TEXT,
    design_prompt TEXT,
    mockup_prompt TEXT,
    dashboard_lane TEXT,
    dashboard_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_saas_dashboard_v80_lane ON saas_dashboard_v80(dashboard_lane);
CREATE INDEX IF NOT EXISTS idx_saas_dashboard_v80_score ON saas_dashboard_v80(dashboard_score DESC);
