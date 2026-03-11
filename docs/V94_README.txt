TrendForge V94 升级包

功能：
- 真实 Feishu Webhook 执行器
- 从 execution_jobs_v93 读取任务
- 推送到 feishu_main / feishu_vip
- 未配置 webhook 自动跳过

运行前建议先配置环境变量：

export FEISHU_MAIN_WEBHOOK='你的主群 webhook'
export FEISHU_VIP_WEBHOOK='你的 VIP 群 webhook'

运行：

cd /root/trendforge-mvp/server

sqlite3 trendforge.db < sql/migrate_v94.sql
python3 engines/feishu_webhook_v94.py
python3 api/feishu_webhook_v94_api.py

发布：

cp /root/trendforge-mvp/web/feishu-webhook-v94.html /var/www/trendforge/
cp /root/trendforge-mvp/web/feishu-webhook-v94.js /var/www/trendforge/
cp /root/trendforge-mvp/server/docs/feishu_webhook_v94.json /var/www/trendforge/docs/

访问：
trendforgepro.com/feishu-webhook-v94.html
