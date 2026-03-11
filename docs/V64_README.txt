TrendForge V64 升级包说明

目录：
- server/sql/migrate_v64.sql
- server/engines/command_center_v64.py
- server/api/command_center_v64_api.py
- server/pipeline/run_v64_pipeline.sh
- web/command-center-v64.html
- web/command-center-v64.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v64.sql
3) python3 engines/command_center_v64.py
4) python3 api/command_center_v64_api.py

发布：
cp /root/trendforge-mvp/web/command-center-v64.html /var/www/trendforge/
cp /root/trendforge-mvp/web/command-center-v64.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/command_center_v64.json /var/www/trendforge/docs/

访问：
trendforgepro.com/command-center-v64.html
