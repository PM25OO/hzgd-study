import requests

# 目标 URL
WATCH_URL = "https://gdypt.rf.hangzhou.gov.cn:9443/ginkgo/system-api/system/videoStudy/data/watchVideo"
FINISH_URL = "https://gdypt.rf.hangzhou.gov.cn:9443/ginkgo/system-api/system/videoStudy/data/finishStudy"

# 填入 Bearer Token
TOKEN = ""

# 设置请求头，模拟浏览器和 PowerShell 中的配置
headers = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Encoding": "gzip, deflate, br, zstd",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5",
    # Authorization will be filled from runtime configuration (env var or CLI)
    "Authorization": "",
    "Cache-Control": "no-cache",
    "Origin": "https://gdypt.rf.hangzhou.gov.cn:9443",
    "Pragma": "no-cache",
    "Referer": "https://gdypt.rf.hangzhou.gov.cn:9443/hzgd-web/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "sec-ch-ua": '"Chromium";v="148", "Microsoft Edge";v="148", "Not/A)Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/148.0.0.0 Safari/537.36 Edg/148.0.0.0"
}


# 创建一个会话对象，相当于 PowerShell 中的 New-Object WebRequestSession
# 它可以自动处理和管理 Cookies，保持会话状态
session = requests.Session()


def ensure_auth_header(token: str) -> str:
    """Normalize token to a full Authorization header value.

    If user passes the raw token, prefix with 'Bearer '. If they pass a full
    header value (starting with 'Bearer '), keep it as-is.
    """
    if not token:
        return ""
    token = token.strip()
    if token.lower().startswith("bearer "):
        return token
    return f"Bearer {token}"


def send_post(url: str, data: dict, headers: dict, timeout: int = 10):
    try:
        return session.post(url, headers=headers, data=data, timeout=timeout)
    except Exception as e:
        print(f"请求 {url} 时发生错误: {e}")
        return None


def main(max_watch_id: int = 410):
    """主函数：
    - 先按 id 从 001 到 max_watch_id 请求 watchVideo（字符串三位零填充）
    - 若返回 JSON 的字段 `data` 存在且有值，则用该值作为 id 请求 finishStudy
    - 无论 finishStudy 返回成功与否，都继续下一轮
    """

    # 填充 Authorization
    auth_header = ensure_auth_header(TOKEN)
    if not auth_header:
        print("未提供 Authorization token，请先在 TOKEN 中填入值。")
        return
    headers["Authorization"] = auth_header

    for i in range(1, max_watch_id + 1):
        watch_id = f"{i:03d}"  # 001, 002, ...
        watch_data = {"id": watch_id}

        resp_watch = send_post(WATCH_URL, watch_data, headers)
        if resp_watch is None:
            # 网络/连接错误，继续下一个 id
            continue

        print(f"watch id={watch_id}, 状态码: {resp_watch.status_code}, 返回内容: {resp_watch.text}")

        # 解析 JSON 并检查 data 字段
        try:
            j = resp_watch.json()
        except Exception:
            j = None

        finish_id = None
        if isinstance(j, dict) and j.get("data"):
            finish_id = j["data"]

        if finish_id:
            finish_data = {"id": finish_id}
            resp_finish = send_post(FINISH_URL, finish_data, headers)
            if resp_finish is None:
                print(f"finish id={finish_id} 请求失败（网络错误）")
            else:
                print(f"finish id={finish_id}, 状态码: {resp_finish.status_code}, 返回内容: {resp_finish.text}")



if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("中断，停止发送请求。")
