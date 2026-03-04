import os
import sqlite3
import hashlib
import random
from datetime import datetime, timedelta

import jwt
from fastapi import Header, HTTPException

BASE_DIR = os.path.dirname(__file__)
DB_PATH = os.path.join(BASE_DIR, "trendforge.db")

# ✅ 生产建议：在 systemd / 环境变量里设置 JWT_SECRET
# 例如：Environment="JWT_SECRET=一个长随机字符串"
JWT_SECRET = os.environ.get("JWT_SECRET", "CHANGE_THIS_TO_RANDOM_SECRET")
JWT_ALGORITHM = "HS256"


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def hash_code(code: str) -> str:
    return hashlib.sha256(code.encode()).hexdigest()


def generate_otp(phone: str) -> str:
    """
    生成 OTP 并写入 otp_codes 表（hash 存储），返回明文 OTP（MVP 测试用）
    """
    code = str(random.randint(100000, 999999))
    code_hash = hash_code(code)
    expires_at = (datetime.utcnow() + timedelta(minutes=5)).isoformat()

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO otp_codes (phone, code_hash, expires_at)
        VALUES (?, ?, ?)
        """,
        (phone, code_hash, expires_at),
    )
    conn.commit()
    conn.close()

    # ⚠️ 测试阶段直接返回验证码；上线后改成发送短信/邮件
    return code


def verify_otp(phone: str, code: str) -> dict:
    """
    校验 OTP，成功则创建用户（如不存在）并签发 JWT
    """
    if not phone or not code:
        raise HTTPException(status_code=400, detail="Missing phone or code")

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT * FROM otp_codes
        WHERE phone = ?
        ORDER BY id DESC
        LIMIT 1
        """,
        (phone,),
    )
    row = cur.fetchone()

    if not row:
        conn.close()
        raise HTTPException(status_code=400, detail="No OTP found")

    # 过期校验
    try:
        expires_at = datetime.fromisoformat(row["expires_at"])
    except Exception:
        conn.close()
        raise HTTPException(status_code=500, detail="OTP expires_at format error")

    if datetime.utcnow() > expires_at:
        # ✅ 过期就顺便删除，减少表垃圾
        cur.execute("DELETE FROM otp_codes WHERE id = ?", (row["id"],))
        conn.commit()
        conn.close()
        raise HTTPException(status_code=400, detail="OTP expired")

    # hash 校验
    if hash_code(code) != row["code_hash"]:
        conn.close()
        raise HTTPException(status_code=400, detail="Invalid code")

    # ✅ 防重放：验证成功立刻删除这条 OTP
    cur.execute("DELETE FROM otp_codes WHERE id = ?", (row["id"],))
    conn.commit()

    # 登录成功 → 创建用户（如不存在）
    cur.execute("SELECT * FROM users WHERE phone = ?", (phone,))
    user = cur.fetchone()

    if not user:
        cur.execute(
            """
            INSERT INTO users (phone, created_at)
            VALUES (?, datetime('now'))
            """,
            (phone,),
        )
        conn.commit()

    # 生成 JWT（7 天有效）
    token = jwt.encode(
        {
            "phone": phone,
            "exp": datetime.utcnow() + timedelta(days=7),
            "iat": datetime.utcnow(),
        },
        JWT_SECRET,
        algorithm=JWT_ALGORITHM,
    )

    conn.close()

    return {"message": "login_success", "token": token}


def get_current_user(authorization: str = Header(None)) -> dict:
    """
    解析 Authorization: Bearer <token>，返回 JWT payload
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing Bearer token")

    token = authorization.split(" ", 1)[1].strip()
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

