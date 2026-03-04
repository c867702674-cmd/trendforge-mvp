import base64
import hashlib
import os
import time
import urllib.parse
import requests
from db import get_conn

OAUTH_TOKEN_URL = "https://api.etsy.com/v3/public/oauth/token"
OAUTH_AUTHORIZE_URL = "https://www.etsy.com/oauth/connect"
API_BASE = "https://api.etsy.com/v3/application"

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")

def generate_pkce_pair() -> tuple[str, str]:
    # code_verifier: high-entropy random string
    code_verifier = _b64url(os.urandom(32))
    challenge = hashlib.sha256(code_verifier.encode("utf-8")).digest()
    code_challenge = _b64url(challenge)
    return code_verifier, code_challenge

def get_oauth_row():
    with get_conn() as conn:
        row = conn.execute("SELECT * FROM etsy_oauth WHERE id=1").fetchone()
        if not row:
            raise RuntimeError("etsy_oauth not initialized. Run the SQL migration first.")
        return dict(row)

def save_oauth_fields(**fields):
    keys = ", ".join([f"{k}=?" for k in fields.keys()])
    vals = list(fields.values())
    vals.append(int(time.time()))
    with get_conn() as conn:
        conn.execute(
            f"UPDATE etsy_oauth SET {keys}, updated_at=? WHERE id=1",
            vals
        )

def build_authorize_url(state: str, code_challenge: str) -> str:
    cfg = get_oauth_row()
    params = {
        "response_type": "code",
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "scope": cfg["scopes"],  # space-separated
        "state": state,
        "code_challenge": code_challenge,
        "code_challenge_method": "S256",
    }
    return OAUTH_AUTHORIZE_URL + "?" + urllib.parse.urlencode(params, quote_via=urllib.parse.quote)

def exchange_code_for_token(code: str, code_verifier: str):
    cfg = get_oauth_row()
    data = {
        "grant_type": "authorization_code",
        "client_id": cfg["client_id"],
        "redirect_uri": cfg["redirect_uri"],
        "code": code,
        "code_verifier": code_verifier,
    }
    resp = requests.post(OAUTH_TOKEN_URL, data=data, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    # Etsy 要求 Authorization 里的 Bearer 前缀包含 numeric user id + "." + access token :contentReference[oaicite:6]{index=6}
    access_token = payload["access_token"]
    refresh_token = payload.get("refresh_token")
    expires_in = int(payload.get("expires_in", 3600))
    expires_at = int(time.time()) + expires_in - 60  # 提前 60 秒刷新

    # 获取 user_id（numeric）
    user_id = get_me_user_id(cfg["client_id"], cfg["shared_secret"], access_token)
    save_oauth_fields(
        user_id=str(user_id),
        access_token=access_token,
        refresh_token=refresh_token,
        access_token_expires_at=expires_at,
    )
    return payload

def refresh_access_token() -> str:
    cfg = get_oauth_row()
    if not cfg.get("refresh_token"):
        raise RuntimeError("No refresh_token found. Run initial authorization first.")
    now = int(time.time())
    if cfg.get("access_token") and cfg.get("access_token_expires_at", 0) > now:
        return cfg["access_token"]

    data = {
        "grant_type": "refresh_token",
        "client_id": cfg["client_id"],
        "refresh_token": cfg["refresh_token"],
    }
    resp = requests.post(OAUTH_TOKEN_URL, data=data, timeout=30)
    resp.raise_for_status()
    payload = resp.json()

    access_token = payload["access_token"]
    expires_in = int(payload.get("expires_in", 3600))
    expires_at = int(time.time()) + expires_in - 60

    # refresh grant 也可能回新 refresh_token（以实际返回为准）
    new_refresh = payload.get("refresh_token") or cfg["refresh_token"]
    user_id = cfg.get("user_id") or str(get_me_user_id(cfg["client_id"], cfg["shared_secret"], access_token))

    save_oauth_fields(
        user_id=str(user_id),
        access_token=access_token,
        refresh_token=new_refresh,
        access_token_expires_at=expires_at,
    )
    return access_token

def etsy_headers(access_token: str) -> dict:
    cfg = get_oauth_row()
    if not cfg.get("user_id"):
        raise RuntimeError("user_id missing. Complete token exchange first.")
    return {
        "x-api-key": f"{cfg['client_id']}:{cfg['shared_secret']}",
        "authorization": f"Bearer {cfg['user_id']}.{access_token}",
    }

def get_me_user_id(client_id: str, shared_secret: str, access_token: str) -> int:
    headers = {
        "x-api-key": f"{client_id}:{shared_secret}",
        # 这里先不拼 user_id，使用 access_token 去 /users/me 取 user_id
        "authorization": f"Bearer 0.{access_token}",
    }
    url = f"{API_BASE}/users/me"
    resp = requests.get(url, headers=headers, timeout=30)
    # 有些实现允许 0.<token> 访问 /users/me；若失败，你就用一次人工把 user_id 填进 etsy_oauth
    resp.raise_for_status()
    j = resp.json()
    return int(j["user_id"])

if __name__ == "__main__":
    # 用法：首次授权
    # 1) 先把 etsy_oauth 表里的 client_id/shared_secret/redirect_uri/scopes 填好
    # 2) python server/etsy_oauth.py
    import secrets

    state = secrets.token_urlsafe(16)
    code_verifier, code_challenge = generate_pkce_pair()
    print("1) Open this URL in browser, authorize:")
    print(build_authorize_url(state, code_challenge))
    print("\n2) After redirect, copy ?code=... value and paste here.")
    code = input("code: ").strip()
    # 可选：你也可以校验 state（如果你把回调 url 的 state 也复制回来）
    exchange_code_for_token(code, code_verifier)
    print("✅ OAuth tokens saved into SQLite etsy_oauth.")