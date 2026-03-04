import os
import json
import time
import urllib.request

def feishu_get_tenant_token(app_id: str, app_secret: str) -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"Feishu token error: {data}")
    return data["tenant_access_token"]

def feishu_send_text(token: str, chat_id: str, text: str):
    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
    body = {
        "receive_id": chat_id,
        "msg_type": "text",
        "content": json.dumps({"text": text}, ensure_ascii=False),
    }
    payload = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {token}"},
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(f"Feishu send error: {data}")

def main():
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    chat_id = os.getenv("FEISHU_ALERT_CHAT_ID")
    msg = os.getenv("ALERT_TEXT", "TrendForge alert")

    if not (app_id and app_secret and chat_id):
        raise SystemExit("Missing FEISHU_APP_ID/FEISHU_APP_SECRET/FEISHU_ALERT_CHAT_ID")

    token = feishu_get_tenant_token(app_id, app_secret)
    feishu_send_text(token, chat_id, msg)

if __name__ == "__main__":
    main()