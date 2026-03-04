# scripts/etsy_oauth_exchange.py
import os
import sys
import requests

TOKEN_URL = "https://openapi.etsy.com/v3/public/oauth/token"

def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: python3 scripts/etsy_oauth_exchange.py <AUTH_CODE>")

    code = sys.argv[1].strip()
    client_id = os.getenv("ETSY_CLIENT_ID", "").strip()
    client_secret = os.getenv("ETSY_CLIENT_SECRET", "").strip()
    redirect_uri = os.getenv("ETSY_REDIRECT_URI", "").strip()

    if not client_id or not client_secret or not redirect_uri:
        raise SystemExit("Missing ETSY_CLIENT_ID / ETSY_CLIENT_SECRET / ETSY_REDIRECT_URI env vars.")

    data = {
        "grant_type": "authorization_code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "code": code,
    }

    # Etsy OAuth token endpoint uses client secret. (Provide via Basic or body; we use Basic)
    resp = requests.post(
        TOKEN_URL,
        data=data,
        auth=(client_id, client_secret),
        timeout=30,
    )
    try:
        j = resp.json()
    except Exception:
        raise SystemExit(f"Token exchange failed (non-json): {resp.status_code} {resp.text}")

    if resp.status_code >= 400:
        raise SystemExit(f"Token exchange failed: {resp.status_code} {j}")

    # Print tokens for you to store into .env.etsy (IMPORTANT: keep secret)
    print("=== SUCCESS ===")
    print("access_token:", j.get("access_token"))
    print("refresh_token:", j.get("refresh_token"))
    print("expires_in:", j.get("expires_in"))

if __name__ == "__main__":
    main()