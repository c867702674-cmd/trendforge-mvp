TrendForge V93 升级包

功能：Execution Engine
自动执行 Automation Hub 产生的任务。

运行：

cd /root/trendforge-mvp/server

sqlite3 trendforge.db < sql/migrate_v93.sql
python3 engines/execution_engine_v93.py
python3 api/execution_engine_v93_api.py

发布：

cp /root/trendforge-mvp/web/execution-engine-v93.html /var/www/trendforge/
cp /root/trendforge-mvp/web/execution-engine-v93.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/execution_engine_v93.json /var/www/trendforge/docs/

访问：

trendforgepro.com/execution-engine-v93.html
