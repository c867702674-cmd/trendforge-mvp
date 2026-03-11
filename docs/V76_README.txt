TrendForge V76 升级包说明

目录：
- server/sql/migrate_v76.sql
- server/engines/launch_orchestrator_v76.py
- server/api/launch_orchestrator_v76_api.py
- server/pipeline/run_v76_pipeline.sh
- web/launch-orchestrator-v76.html
- web/launch-orchestrator-v76.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v76.sql
3) python3 engines/launch_orchestrator_v76.py
4) python3 api/launch_orchestrator_v76_api.py

发布：
cp /root/trendforge-mvp/web/launch-orchestrator-v76.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-orchestrator-v76.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_orchestrator_v76.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-orchestrator-v76.html
