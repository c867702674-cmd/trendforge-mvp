TrendForge V60 升级包说明

目录：
- server/sql/migrate_v60.sql
- server/engines/execution_pack_v60.py
- server/api/execution_pack_v60_api.py
- server/pipeline/run_v60_pipeline.sh
- web/execution-pack-v60.html
- web/execution-pack-v60.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v60.sql
3) python3 engines/execution_pack_v60.py
4) python3 api/execution_pack_v60_api.py

发布：
cp /root/trendforge-mvp/web/execution-pack-v60.html /var/www/trendforge/
cp /root/trendforge-mvp/web/execution-pack-v60.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/execution_pack_v60.json /var/www/trendforge/docs/

访问：
trendforgepro.com/execution-pack-v60.html
