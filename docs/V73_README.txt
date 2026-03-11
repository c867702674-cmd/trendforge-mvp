TrendForge V73 升级包说明

目录：
- server/sql/migrate_v73.sql
- server/engines/allocation_board_v73.py
- server/api/allocation_board_v73_api.py
- server/pipeline/run_v73_pipeline.sh
- web/allocation-board-v73.html
- web/allocation-board-v73.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v73.sql
3) python3 engines/allocation_board_v73.py
4) python3 api/allocation_board_v73_api.py

发布：
cp /root/trendforge-mvp/web/allocation-board-v73.html /var/www/trendforge/
cp /root/trendforge-mvp/web/allocation-board-v73.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/allocation_board_v73.json /var/www/trendforge/docs/

访问：
trendforgepro.com/allocation-board-v73.html
