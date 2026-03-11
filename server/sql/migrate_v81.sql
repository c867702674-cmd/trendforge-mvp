-- TrendForge V81 MJ Prompt Engine
CREATE TABLE IF NOT EXISTS mj_prompt_v81 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_ai_id INTEGER,
    saas_dashboard_id INTEGER,
    release_command_id INTEGER,
    product_type TEXT,
    priority_tier TEXT,
    risk_level TEXT,
    safe_term TEXT,
    title_en TEXT,
    sku_code TEXT,
    design_style TEXT,
    mj_prompt TEXT,
    negative_prompt TEXT,
    mockup_prompt TEXT,
    prompt_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_mj_prompt_v81_product ON mj_prompt_v81(product_type);
CREATE INDEX IF NOT EXISTS idx_mj_prompt_v81_score ON mj_prompt_v81(prompt_score DESC);
