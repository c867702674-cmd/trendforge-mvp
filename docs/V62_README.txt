TrendForge V62 升级包说明

目录：
- server/sql/migrate_v62.sql
- server/engines/publish_board_v62.py
- server/api/publish_board_v62_api.py
- server/pipeline/run_v62_pipeline.sh
- web/publish-board-v62.html
- web/publish-board-v62.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v62.sql
3) python3 engines/publish_board_v62.py
4) python3 api/publish_board_v62_api.py

发布：
cp /root/trendforge-mvp/web/publish-board-v62.html /var/www/trendforge/
cp /root/trendforge-mvp/web/publish-board-v62.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/publish_board_v62.json /var/www/trendforge/docs/

访问：
trendforgepro.com/publish-board-v62.html
