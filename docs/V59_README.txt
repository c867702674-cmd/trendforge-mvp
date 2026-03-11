TrendForge V59 升级包说明

目录：
- server/sql/migrate_v59.sql
- server/engines/listing_generator_v59.py
- server/api/listing_v59_api.py
- server/pipeline/run_v59_pipeline.sh
- web/listing-v59.html
- web/listing-v59.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v59.sql
3) python3 engines/listing_generator_v59.py
4) python3 api/listing_v59_api.py

发布：
cp /root/trendforge-mvp/web/listing-v59.html /var/www/trendforge/
cp /root/trendforge-mvp/web/listing-v59.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/listing_v59.json /var/www/trendforge/docs/

访问：
trendforgepro.com/listing-v59.html
