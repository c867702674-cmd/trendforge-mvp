TrendForge V70 升级包说明

目录：
- server/sql/migrate_v70.sql
- server/engines/strategic_hub_v70.py
- server/api/strategic_hub_v70_api.py
- server/pipeline/run_v70_pipeline.sh
- web/strategic-hub-v70.html
- web/strategic-hub-v70.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v70.sql
3) python3 engines/strategic_hub_v70.py
4) python3 api/strategic_hub_v70_api.py

发布：
cp /root/trendforge-mvp/web/strategic-hub-v70.html /var/www/trendforge/
cp /root/trendforge-mvp/web/strategic-hub-v70.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/strategic_hub_v70.json /var/www/trendforge/docs/

访问：
trendforgepro.com/strategic-hub-v70.html
