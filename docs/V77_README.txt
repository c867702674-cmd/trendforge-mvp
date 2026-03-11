TrendForge V77 升级包说明

目录：
- server/sql/migrate_v77.sql
- server/engines/launch_control_v77.py
- server/api/launch_control_v77_api.py
- server/pipeline/run_v77_pipeline.sh
- web/launch-control-v77.html
- web/launch-control-v77.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v77.sql
3) python3 engines/launch_control_v77.py
4) python3 api/launch_control_v77_api.py

发布：
cp /root/trendforge-mvp/web/launch-control-v77.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-control-v77.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_control_v77.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-control-v77.html
