TrendForge V71 升级包说明

目录：
- server/sql/migrate_v71.sql
- server/engines/executive_grid_v71.py
- server/api/executive_grid_v71_api.py
- server/pipeline/run_v71_pipeline.sh
- web/executive-grid-v71.html
- web/executive-grid-v71.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v71.sql
3) python3 engines/executive_grid_v71.py
4) python3 api/executive_grid_v71_api.py

发布：
cp /root/trendforge-mvp/web/executive-grid-v71.html /var/www/trendforge/
cp /root/trendforge-mvp/web/executive-grid-v71.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/executive_grid_v71.json /var/www/trendforge/docs/

访问：
trendforgepro.com/executive-grid-v71.html
