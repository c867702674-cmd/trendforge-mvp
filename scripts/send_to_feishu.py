# scripts/send_to_feishu.py
import json
import os
import subprocess
from typing import Any, Dict, Optional

import requests


def _get_token() -> str:
    """
    Get tenant_access_token by calling existing helper script.
    Requires env: FEISHU_APP_ID, FEISHU_APP_SECRET
    """
    # Prefer running the project's token script so behavior stays consistent
    # NOTE: this file is under scripts/, so "scripts/get_feishu_token.py" path works when cwd is project root
    out = subprocess.check_output(["python3", "scripts/get_feishu_token.py"], text=True).strip()
    if not out:
        raise RuntimeError("Empty token returned from scripts/get_feishu_token.py")
    return out


def _post_message(
    *,
    receive_id: str,
    receive_id_type: str,
    msg_type: str,
    content_obj: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Send message to Feishu.
    content_obj will be JSON-dumped into the 'content' string that Feishu expects.
    """
    token = _get_token()
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json; charset=utf-8",
    }

    payload = {
        "receive_id": receive_id,
        "msg_type": msg_type,
        "content": json.dumps(content_obj, ensure_ascii=False),
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=20)
    data = resp.json()

    if data.get("code") != 0:
        # Make debugging easy
        raise RuntimeError(f"Send message failed: {data}")

    return data


def send_text(text: str, chat_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Send plain text message.
    env: FEISHU_CHAT_ID (if chat_id not provided)
    """
    chat_id = chat_id or os.getenv("FEISHU_CHAT_ID")
    if not chat_id:
        raise RuntimeError("FEISHU_CHAT_ID not set (or pass chat_id explicitly).")

    return _post_message(
        receive_id=chat_id,
        receive_id_type="chat_id",
        msg_type="text",
        content_obj={"text": text},
    )


def send_card(card: Dict[str, Any], chat_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Send interactive card message.
    env: FEISHU_CHAT_ID (if chat_id not provided)
    """
    chat_id = chat_id or os.getenv("FEISHU_CHAT_ID")
    if not chat_id:
        raise RuntimeError("FEISHU_CHAT_ID not set (or pass chat_id explicitly).")

    return _post_message(
        receive_id=chat_id,
        receive_id_type="chat_id",
        msg_type="interactive",
        content_obj=card,
    )