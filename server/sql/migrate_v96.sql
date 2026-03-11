CREATE TABLE IF NOT EXISTS listing_drafts_v96 (
id INTEGER PRIMARY KEY AUTOINCREMENT,
trend_id INTEGER,
source_term TEXT,
product_type TEXT,
title TEXT,
tags TEXT,
description TEXT,
sku TEXT,
status TEXT
);
