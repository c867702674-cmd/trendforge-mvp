TrendForge V67 升级包说明

目录：
- server/sql/migrate_v67.sql
- server/engines/control_tower_v67.py
- server/api/control_tower_v67_api.py
- server/pipeline/run_v67_pipeline.sh
- web/control-tower-v67.html
- web/control-tower-v67.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v67.sql
3) python3 engines/control_tower_v67.py
4) python3 api/control_tower_v67_api.py

发布：
cp /root/trendforge-mvp/web/control-tower-v67.html /var/www/trendforge/
cp /root/trendforge-mvp/web/control-tower-v67.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/control_tower_v67.json /var/www/trendforge/docs/

访问：
trendforgepro.com/control-tower-v67.html
