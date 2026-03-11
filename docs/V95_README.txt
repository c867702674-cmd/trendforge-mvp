TrendForge V95 升级包

功能：
- 飞书卡片升级版
- 根据 trend_data_v89 直接生成更完整的 Feishu 卡片
- DO_NOW -> VIP 群
- WATCH -> Main 群

运行前建议先配置环境变量：

export FEISHU_MAIN_WEBHOOK='你的主群 webhook'
export FEISHU_VIP_WEBHOOK='你的 VIP 群 webhook'

运行：

cd /root/trendforge-mvp/server

sqlite3 trendforge.db < sql/migrate_v95.sql
python3 engines/feishu_card_v95.py
python3 api/feishu_card_v95_api.py

发布：

cp /root/trendforge-mvp/web/feishu-card-v95.html /var/www/trendforge/
cp /root/trendforge-mvp/web/feishu-card-v95.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/feishu_card_v95.json /var/www/trendforge/docs/

访问：
trendforgepro.com/feishu-card-v95.html
