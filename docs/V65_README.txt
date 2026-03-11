TrendForge V65 升级包说明

目录：
- server/sql/migrate_v65.sql
- server/engines/batch_studio_v65.py
- server/api/batch_studio_v65_api.py
- server/pipeline/run_v65_pipeline.sh
- web/batch-studio-v65.html
- web/batch-studio-v65.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v65.sql
3) python3 engines/batch_studio_v65.py
4) python3 api/batch_studio_v65_api.py

发布：
cp /root/trendforge-mvp/web/batch-studio-v65.html /var/www/trendforge/
cp /root/trendforge-mvp/web/batch-studio-v65.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/batch_studio_v65.json /var/www/trendforge/docs/

访问：
trendforgepro.com/batch-studio-v65.html
