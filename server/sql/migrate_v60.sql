-- TrendForge V60 Execution Pack Engine
CREATE TABLE IF NOT EXISTS execution_packs_v60 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    listing_id INTEGER,
    source_term TEXT,
    safe_term TEXT,
    risk_level TEXT,
    product_type TEXT,
    title_en TEXT,
    tags_en TEXT,
    bullets_en TEXT,
    description_en TEXT,
    design_prompt_en TEXT,
    sku_code TEXT,
    execution_pack_text TEXT,
    pack_score REAL DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_execution_v60_listing_id
ON execution_packs_v60(listing_id);

CREATE INDEX IF NOT EXISTS idx_execution_v60_product_type
ON execution_packs_v60(product_type);

CREATE INDEX IF NOT EXISTS idx_execution_v60_score
ON execution_packs_v60(pack_score DESC);
