TrendForge V74 升级包说明

目录：
- server/sql/migrate_v74.sql
- server/engines/release_routing_v74.py
- server/api/release_routing_v74_api.py
- server/pipeline/run_v74_pipeline.sh
- web/release-routing-v74.html
- web/release-routing-v74.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v74.sql
3) python3 engines/release_routing_v74.py
4) python3 api/release_routing_v74_api.py

发布：
cp /root/trendforge-mvp/web/release-routing-v74.html /var/www/trendforge/
cp /root/trendforge-mvp/web/release-routing-v74.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/release_routing_v74.json /var/www/trendforge/docs/

访问：
trendforgepro.com/release-routing-v74.html
