TrendForge V82 升级包说明

目录：
- server/sql/migrate_v82.sql
- server/engines/launch_readiness_v82.py
- server/api/launch_readiness_v82_api.py
- server/pipeline/run_v82_pipeline.sh
- web/launch-readiness-v82.html
- web/launch-readiness-v82.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v82.sql
3) python3 engines/launch_readiness_v82.py
4) python3 api/launch_readiness_v82_api.py

发布：
cp /root/trendforge-mvp/web/launch-readiness-v82.html /var/www/trendforge/
cp /root/trendforge-mvp/web/launch-readiness-v82.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/launch_readiness_v82.json /var/www/trendforge/docs/

访问：
trendforgepro.com/launch-readiness-v82.html
