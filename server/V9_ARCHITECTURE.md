TrendForge V9 Architecture
Goal:
Move TrendForge from a flat file layout into a modular structure.
Recommended structure:
/root/trendforge-mvp/server/
├─ pipeline/
│  ├─ run_v7_pipeline.sh
│  ├─ run_v8_pipeline.sh
│  ├─ run_v85_pipeline.sh
│  └─ run_v9_pipeline.sh
├─ sources/
│  ├─ fetch_trends_rss.py
│  ├─ fetch_google_trends_serpapi.py
│  ├─ fetch_etsy_pod.py
│  ├─ fetch_etsy_pod_v2.py
│  ├─ fetch_amazon_movers_v1.py
│  ├─ fetch_amazon_pod_terms_v2.py
│  └─ fetch_tiktok_pod_trends_v1.py
├─ engines/
│  ├─ build_trends_from_raw.py
│  ├─ trend_filter_pod.py
│  ├─ trend_filter_pod_v2.py
│  ├─ trend_expansion_engine.py
│  ├─ trend_expansion_engine_v2.py
│  ├─ mj_prompt_generator.py
│  └─ extract_pod_keywords.py
├─ push/
│  ├─ push_trends_feishu.py
│  ├─ push_trends_feishu_v7.py
│  ├─ push_trends_feishu_v711.py
│  └─ execution_pack.py
├─ sql/
│  ├─ create_design_ideas.sql
│  ├─ migrate_v7.sql
│  ├─ migrate_v8.sql
│  └─ migrate_v85.sql
├─ docs/
└─ legacy_root/
V9 wrapper pipeline order:
sql/migrate_v85.sql
sources/fetch_google_trends_serpapi.py
sources/fetch_etsy_pod_v2.py
sources/fetch_amazon_pod_terms_v2.py
sources/fetch_tiktok_pod_trends_v1.py
engines/extract_pod_keywords.py
engines/build_trends_from_raw.py
engines/trend_expansion_engine_v2.py
engines/mj_prompt_generator.py
push/push_trends_feishu_v711.py