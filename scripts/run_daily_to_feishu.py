def _col_to_a1(n: int) -> str:
    """1 -> A, 2 -> B, ... 26 -> Z, 27 -> AA ..."""
    s = ""
    while n > 0:
        n, r = divmod(n - 1, 26)
        s = chr(65 + r) + s
    return s

def append_rows_to_feishu(token: str, sheet_id: str, rows: list[list]):
    """
    关键：range 必须覆盖“实际写入的行数/列数”
    否则会报 90202: rows/cols of value > range
    """
    url = f"https://open.feishu.cn/open-apis/sheets/v2/spreadsheets/{FEISHU_SPREADSHEET_TOKEN}/values_append"
    headers = {"Authorization": f"Bearer {token}"}

    if not rows:
        return

    row_count = len(rows)
    col_count = max(len(r) for r in rows)  # 例如你现在是 10 列
    end_col = _col_to_a1(col_count)        # 10 -> J

    # ✅ range 覆盖从A1到“实际列+实际行”
    rng = f"{sheet_id}!A1:{end_col}{row_count}"

    payload = {
        "valueRange": {
            "range": rng,
            "values": rows,
        },
        "insertDataOption": "INSERT_ROWS",
        "valueInputOption": "USER_ENTERED",
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    data = resp.json()
    if data.get("code") != 0:
        raise RuntimeError(f"Feishu append failed: {data}")
    return data