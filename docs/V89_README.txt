TrendForge V89 升级包说明

目录：
- server/sql/migrate_v89.sql
- server/engines/trend_data_v89.py
- server/api/trend_data_v89_api.py
- server/pipeline/run_v89_pipeline.sh
- web/trend-data-v89.html
- web/trend-data-v89.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v89.sql
3) python3 engines/trend_data_v89.py
4) python3 api/trend_data_v89_api.py

发布：
cp /root/trendforge-mvp/web/trend-data-v89.html /var/www/trendforge/
cp /root/trendforge-mvp/web/trend-data-v89.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/trend_data_v89.json /var/www/trendforge/docs/

访问：
trendforgepro.com/trend-data-v89.html

说明：
- 当前是 seed 版真实结构，占位 Google Trends / Etsy / Amazon Movers 三路数据
- 下一步可替换为 pytrends、Etsy API、Amazon 数据源
