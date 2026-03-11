TrendForge V91 升级包说明

目录：
- server/sql/migrate_v91.sql
- server/engines/push_center_v91.py
- server/api/push_center_v91_api.py
- server/pipeline/run_v91_pipeline.sh
- web/push-center-v91.html
- web/push-center-v91.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v91.sql
3) python3 engines/push_center_v91.py
4) python3 api/push_center_v91_api.py

发布：
cp /root/trendforge-mvp/web/push-center-v91.html /var/www/trendforge/
cp /root/trendforge-mvp/web/push-center-v91.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/push_center_v91.json /var/www/trendforge/docs/

访问：
trendforgepro.com/push-center-v91.html
