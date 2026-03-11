TrendForge V85 升级包说明

目录：
- server/sql/migrate_v85.sql
- server/engines/commercial_launch_v85.py
- server/api/commercial_launch_v85_api.py
- server/pipeline/run_v85_pipeline.sh
- web/commercial-launch-v85.html
- web/commercial-launch-v85.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v85.sql
3) python3 engines/commercial_launch_v85.py
4) python3 api/commercial_launch_v85_api.py

发布：
cp /root/trendforge-mvp/web/commercial-launch-v85.html /var/www/trendforge/
cp /root/trendforge-mvp/web/commercial-launch-v85.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/commercial_launch_v85.json /var/www/trendforge/docs/

访问：
trendforgepro.com/commercial-launch-v85.html
