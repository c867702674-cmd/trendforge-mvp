TrendForge V69 升级包说明

目录：
- server/sql/migrate_v69.sql
- server/engines/operations_hq_v69.py
- server/api/operations_hq_v69_api.py
- server/pipeline/run_v69_pipeline.sh
- web/operations-hq-v69.html
- web/operations-hq-v69.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v69.sql
3) python3 engines/operations_hq_v69.py
4) python3 api/operations_hq_v69_api.py

发布：
cp /root/trendforge-mvp/web/operations-hq-v69.html /var/www/trendforge/
cp /root/trendforge-mvp/web/operations-hq-v69.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/operations_hq_v69.json /var/www/trendforge/docs/

访问：
trendforgepro.com/operations-hq-v69.html
