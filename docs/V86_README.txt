TrendForge V86 升级包说明

目录：
- server/sql/migrate_v86.sql
- server/engines/launch_ops_v86.py
- server/api/launch_ops_v86_api.py
- server/pipeline/run_v86_pipeline.sh
- web/launch-ops-v86.html
- web/launch-ops-v86.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v86.sql
3) python3 engines/launch_ops_v86.py
4) python3 api/launch_ops_v86_api.py

发布：
cp /root/trendforge-mvp/web/launch-ops-v86.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-ops-v86.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_ops_v86.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-ops-v86.html
