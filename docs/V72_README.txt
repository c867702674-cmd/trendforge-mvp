TrendForge V72 升级包说明

目录：
- server/sql/migrate_v72.sql
- server/engines/portfolio_matrix_v72.py
- server/api/portfolio_matrix_v72_api.py
- server/pipeline/run_v72_pipeline.sh
- web/portfolio-matrix-v72.html
- web/portfolio-matrix-v72.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v72.sql
3) python3 engines/portfolio_matrix_v72.py
4) python3 api/portfolio_matrix_v72_api.py

发布：
cp /root/trendforge-mvp/web/portfolio-matrix-v72.html /var/www/trendforge/
cp /root/trendforge-mvp/web/portfolio-matrix-v72.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/portfolio_matrix_v72.json /var/www/trendforge/docs/

访问：
trendforgepro.com/portfolio-matrix-v72.html
