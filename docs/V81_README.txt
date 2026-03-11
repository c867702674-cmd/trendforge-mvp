TrendForge V81 升级包说明

目录：
- server/sql/migrate_v81.sql
- server/engines/mj_prompt_v81.py
- server/api/mj_prompt_v81_api.py
- server/pipeline/run_v81_pipeline.sh
- web/mj-prompt-v81.html
- web/mj-prompt-v81.js

运行：
1) cd /root/trendforge-mvp/server
2) sqlite3 trendforge.db < sql/migrate_v81.sql
3) python3 engines/mj_prompt_v81.py
4) python3 api/mj_prompt_v81_api.py

发布：
cp /root/trendforge-mvp/web/mj-prompt-v81.html /var/www/trendforge/
cp /root/trendforge-mvp/web/mj-prompt-v81.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/mj_prompt_v81.json /var/www/trendforge/docs/

访问：
trendforgepro.com/mj-prompt-v81.html
