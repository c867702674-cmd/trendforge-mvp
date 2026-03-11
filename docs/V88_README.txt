TrendForge V88 升级包说明

目录：
- server/sql/migrate_v88.sql
- server/engines/user_system_v88.py
- server/api/user_system_v88_api.py
- server/pipeline/run_v88_pipeline.sh
- web/user-system-v88.html
- web/user-system-v88.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v88.sql
3) python3 engines/user_system_v88.py
4) python3 api/user_system_v88_api.py

发布：
cp /root/trendforge-mvp/web/user-system-v88.html /var/www/trendforge/
cp /root/trendforge-mvp/web/user-system-v88.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/user_system_v88.json /var/www/trendforge/docs/

访问：
trendforgepro.com/user-system-v88.html

演示账号：
- demo_free@trendforge.ai / TrendForge123
- demo_pro@trendforge.ai / TrendForge123
- demo_vip@trendforge.ai / TrendForge123
