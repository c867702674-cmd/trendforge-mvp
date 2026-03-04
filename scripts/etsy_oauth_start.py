# scripts/etsy_oauth_start.py
import os
import secrets
import urllib.parse

AUTH_URL = "https://www.etsy.com/oauth/connect"

def main():
    client_id = os.getenv("ETSY_CLIENT_ID", "").strip()
    redirect_uri = os.getenv("ETSY_REDIRECT_URI", "").strip()
    scope = os.getenv("ETSY_SCOPE", "listings_r").strip()

    if not client_id or not redirect_uri:
        raise SystemExit("Missing ETSY_CLIENT_ID or ETSY_REDIRECT_URI env var.")

    state = secrets.token_urlsafe(24)

    params = {
        "response_type": "code",
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }

    url = AUTH_URL + "?" + urllib.parse.urlencode(params)
    print("Open this URL in your browser, then authorize:")
    print(url)
    print("\nAfter authorization, copy the ?code=... value from redirect URL.")
    print(f"State (optional check): {state}")

if __name__ == "__main__":
    main()