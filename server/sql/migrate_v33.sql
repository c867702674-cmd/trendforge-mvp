CREATE TABLE IF NOT EXISTS opportunity_cards (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 term TEXT,
 card_title TEXT,
 card_subtitle TEXT,
 opportunity_score REAL,
 design_direction TEXT,
 recommended_products_json TEXT,
 recommended_title TEXT,
 image_prompt TEXT,
 payload_json TEXT,
 created_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_opportunity_cards_term
ON opportunity_cards(term);
