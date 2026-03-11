TrendForge V84 升级包说明

目录：
- server/sql/migrate_v84.sql
- server/engines/launch_checklist_v84.py
- server/api/launch_checklist_v84_api.py
- server/pipeline/run_v84_pipeline.sh
- web/launch-checklist-v84.html
- web/launch-checklist-v84.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v84.sql
3) python3 engines/launch_checklist_v84.py
4) python3 api/launch_checklist_v84_api.py

发布：
cp /root/trendforge-mvp/web/launch-checklist-v84.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-checklist-v84.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_checklist_v84.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-checklist-v84.html
