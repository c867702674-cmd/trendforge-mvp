import os
import requests

APP_ID = os.getenv("FEISHU_APP_ID", "")
APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
SPREADSHEET_TOKEN = os.getenv("FEISHU_SPREADSHEET_TOKEN", "")

def get_tenant_access_token() -> str:
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    r = requests.post(url, json={"app_id": APP_ID, "app_secret": APP_SECRET}, timeout=20)
    r.raise_for_status()
    data = r.json()
    if data.get("code") != 0:
        raise RuntimeError(data)
    return data["tenant_access_token"]

def main():
    if not (APP_ID and APP_SECRET and SPREADSHEET_TOKEN):
        raise RuntimeError("Missing env: FEISHU_APP_ID/FEISHU_APP_SECRET/FEISHU_SPREADSHEET_TOKEN")

    token = get_tenant_access_token()
    url = f"https://open.feishu.cn/open-apis/sheets/v3/spreadsheets/{SPREADSHEET_TOKEN}/sheets/query"
    r = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=20)
    r.raise_for_status()
    print(r.json())

if __name__ == "__main__":
    main()