TrendForge V92 升级包说明

目录：
- server/sql/migrate_v92.sql
- server/engines/automation_hub_v92.py
- server/api/automation_hub_v92_api.py
- server/pipeline/run_v92_pipeline.sh
- web/automation-hub-v92.html
- web/automation-hub-v92.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v92.sql
3) python3 engines/automation_hub_v92.py
4) python3 api/automation_hub_v92_api.py

发布：
cp /root/trendforge-mvp/web/automation-hub-v92.html /var/www/trendforge/
cp /root/trendforge-mvp/web/automation-hub-v92.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/automation_hub_v92.json /var/www/trendforge/docs/

访问：
trendforgepro.com/automation-hub-v92.html
