TrendForge V61 升级包说明

目录：
- server/sql/migrate_v61.sql
- server/engines/launch_queue_v61.py
- server/api/launch_queue_v61_api.py
- server/pipeline/run_v61_pipeline.sh
- web/launch-queue-v61.html
- web/launch-queue-v61.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v61.sql
3) python3 engines/launch_queue_v61.py
4) python3 api/launch_queue_v61_api.py

发布：
cp /root/trendforge-mvp/web/launch-queue-v61.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-queue-v61.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_queue_v61.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-queue-v61.html
