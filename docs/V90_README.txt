TrendForge V90 升级包说明

目录：
- server/sql/migrate_v90.sql
- server/engines/billing_system_v90.py
- server/api/billing_system_v90_api.py
- server/pipeline/run_v90_pipeline.sh
- web/billing-system-v90.html
- web/billing-system-v90.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v90.sql
3) python3 engines/billing_system_v90.py
4) python3 api/billing_system_v90_api.py

发布：
cp /root/trendforge-mvp/web/billing-system-v90.html /var/www/trendforge/
cp /root/trendforge-mvp/web/billing-system-v90.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/billing_system_v90.json /var/www/trendforge/docs/

访问：
trendforgepro.com/billing-system-v90.html
