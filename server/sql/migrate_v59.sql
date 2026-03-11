-- TrendForge V59 POD Listing Generator
CREATE TABLE IF NOT EXISTS listing_candidates_v59 (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_term TEXT,
    candidate_term TEXT,
    safe_term TEXT,
    risk_level TEXT,
    product_type TEXT,
    style_hint TEXT,
    audience_hint TEXT,
    title_en TEXT,
    tags_en TEXT,
    bullets_en TEXT,
    description_en TEXT,
    design_prompt_en TEXT,
    sku_code TEXT,
    listing_score REAL DEFAULT 0,
    source_payload_json TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_listing_v59_risk_level
ON listing_candidates_v59(risk_level);

CREATE INDEX IF NOT EXISTS idx_listing_v59_product_type
ON listing_candidates_v59(product_type);

CREATE INDEX IF NOT EXISTS idx_listing_v59_safe_term
ON listing_candidates_v59(safe_term);
