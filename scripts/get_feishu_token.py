import os
import requests

APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")

if not APP_ID or not APP_SECRET:
    raise RuntimeError("FEISHU_APP_ID / FEISHU_APP_SECRET not set")

url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"

resp = requests.post(url, json={
    "app_id": APP_ID,
    "app_secret": APP_SECRET
})

data = resp.json()

if data.get("code") != 0:
    raise RuntimeError(data)

print(data["tenant_access_token"])


