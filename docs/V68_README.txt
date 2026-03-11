TrendForge V68 升级包说明

目录：
- server/sql/migrate_v68.sql
- server/engines/war_room_v68.py
- server/api/war_room_v68_api.py
- server/pipeline/run_v68_pipeline.sh
- web/war-room-v68.html
- web/war-room-v68.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v68.sql
3) python3 engines/war_room_v68.py
4) python3 api/war_room_v68_api.py

发布：
cp /root/trendforge-mvp/web/war-room-v68.html /var/www/trendforge/
cp /root/trendforge-mvp/web/war-room-v68.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/war_room_v68.json /var/www/trendforge/docs/

访问：
trendforgepro.com/war-room-v68.html
