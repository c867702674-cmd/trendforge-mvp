TrendForge V87 升级包说明

目录：
- server/sql/migrate_v87.sql
- server/engines/command_center_v87.py
- server/api/command_center_v87_api.py
- server/pipeline/run_v87_pipeline.sh
- web/command-center-v87.html
- web/command-center-v87.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v87.sql
3) python3 engines/command_center_v87.py
4) python3 api/command_center_v87_api.py

发布：
cp /root/trendforge-mvp/web/command-center-v87.html /var/www/trendforge/
cp /root/trendforge-mvp/web/command-center-v87.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/command_center_v87.json /var/www/trendforge/docs/

访问：
trendforgepro.com/command-center-v87.html
