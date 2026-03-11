TrendForge V63 升级包说明

目录：
- server/sql/migrate_v63.sql
- server/engines/ops_dashboard_v63.py
- server/api/ops_dashboard_v63_api.py
- server/pipeline/run_v63_pipeline.sh
- web/ops-dashboard-v63.html
- web/ops-dashboard-v63.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v63.sql
3) python3 engines/ops_dashboard_v63.py
4) python3 api/ops_dashboard_v63_api.py

发布：
cp /root/trendforge-mvp/web/ops-dashboard-v63.html /var/www/trendforge/
cp /root/trendforge-mvp/web/ops-dashboard-v63.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/ops_dashboard_v63.json /var/www/trendforge/docs/

访问：
trendforgepro.com/ops-dashboard-v63.html
