TrendForge V66 升级包说明

目录：
- server/sql/migrate_v66.sql
- server/engines/mission_planner_v66.py
- server/api/mission_planner_v66_api.py
- server/pipeline/run_v66_pipeline.sh
- web/mission-planner-v66.html
- web/mission-planner-v66.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v66.sql
3) python3 engines/mission_planner_v66.py
4) python3 api/mission_planner_v66_api.py

发布：
cp /root/trendforge-mvp/web/mission-planner-v66.html /var/www/trendforge/
cp /root/trendforge-mvp/web/mission-planner-v66.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/mission_planner_v66.json /var/www/trendforge/docs/

访问：
trendforgepro.com/mission-planner-v66.html
