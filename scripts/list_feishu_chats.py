import os, json, urllib.request

def get_token(app_id, app_secret):
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = json.dumps({"app_id": app_id, "app_secret": app_secret}).encode("utf-8")
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("code") != 0:
        raise RuntimeError(data)
    return data["tenant_access_token"]

def list_chats(token, page_token=None):
    # 这个接口需要你的应用有“读取群列表/群信息”权限
    base = "https://open.feishu.cn/open-apis/im/v1/chats"
    url = base + (f"?page_token={page_token}" if page_token else "")
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    app_id = os.getenv("FEISHU_APP_ID")
    app_secret = os.getenv("FEISHU_APP_SECRET")
    if not app_id or not app_secret:
        raise SystemExit("Missing FEISHU_APP_ID/FEISHU_APP_SECRET")

    token = get_token(app_id, app_secret)

    all_items = []
    page_token = None
    for _ in range(5):  # 最多翻 5 页
        data = list_chats(token, page_token)
        if data.get("code") != 0:
            raise RuntimeError(data)
        items = data.get("data", {}).get("items", [])
        all_items.extend(items)
        page_token = data.get("data", {}).get("page_token")
        if not page_token:
            break

    # 打印群名 + chat_id（你复制一个你要报警的群）
    for c in all_items:
        name = c.get("name")
        chat_id = c.get("chat_id")
        print(f"{name}\t{chat_id}")

if __name__ == "__main__":
    main()