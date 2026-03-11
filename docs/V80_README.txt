TrendForge V80 升级包说明

目录：
- server/sql/migrate_v80.sql
- server/engines/saas_dashboard_v80.py
- server/api/saas_dashboard_v80_api.py
- server/pipeline/run_v80_pipeline.sh
- web/saas-dashboard-v80.html
- web/saas-dashboard-v80.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v80.sql
3) python3 engines/saas_dashboard_v80.py
4) python3 api/saas_dashboard_v80_api.py

发布：
cp /root/trendforge-mvp/web/saas-dashboard-v80.html /var/www/trendforge/
cp /root/trendforge-mvp/web/saas-dashboard-v80.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/saas_dashboard_v80.json /var/www/trendforge/docs/

访问：
trendforgepro.com/saas-dashboard-v80.html
