TrendForge V75 升级包说明

目录：
- server/sql/migrate_v75.sql
- server/engines/dispatch_center_v75.py
- server/api/dispatch_center_v75_api.py
- server/pipeline/run_v75_pipeline.sh
- web/dispatch-center-v75.html
- web/dispatch-center-v75.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v75.sql
3) python3 engines/dispatch_center_v75.py
4) python3 api/dispatch_center_v75_api.py

发布：
cp /root/trendforge-mvp/web/dispatch-center-v75.html /var/www/trendforge/
cp /root/trendforge-mvp/web/dispatch-center-v75.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/dispatch_center_v75.json /var/www/trendforge/docs/

访问：
trendforgepro.com/dispatch-center-v75.html
