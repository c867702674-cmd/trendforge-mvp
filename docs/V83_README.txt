TrendForge V83 升级包说明

目录：
- server/sql/migrate_v83.sql
- server/engines/commercial_golive_v83.py
- server/api/commercial_golive_v83_api.py
- server/pipeline/run_v83_pipeline.sh
- web/commercial-golive-v83.html
- web/commercial-golive-v83.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v83.sql
3) python3 engines/commercial_golive_v83.py
4) python3 api/commercial_golive_v83_api.py

发布：
cp /root/trendforge-mvp/web/commercial-golive-v83.html /var/www/trendforge/
cp /root/trendforge-mvp/web/commercial-golive-v83.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/commercial_golive_v83.json /var/www/trendforge/docs/

访问：
trendforgepro.com/commercial-golive-v83.html
