"""
第七课：Session 和 Cookie —— 让爬虫保持登录状态
"""

import requests

# ============ 不用 Session 的情况 ============
print("=== 不用 Session（每次都是新连接） ===")
r1 = requests.get("http://httpbin.org/cookies/set?name=zhangsan")
print("第一次请求后的 cookies:", r1.cookies.get_dict())

r2 = requests.get("http://httpbin.org/cookies")
print("第二次请求看到的 cookies:", r2.cookies.get_dict())
# 第二次看不到第一次设置的 cookie！因为两次是独立的请求

print()

# ============ 用 Session ============
print("=== 用 Session（同一个会话） ===")
s = requests.Session()

s.get("http://httpbin.org/cookies/set?name=zhangsan")
r3 = s.get("http://httpbin.org/cookies")
print("用 Session 后能看到 cookie:", r3.text)
# Session 会自动记住之前设置的所有 cookie

print()

# ============ 实战场景：登录后爬取 ============
print("=== 模拟登录流程 ===")

login_session = requests.Session()

# 模拟登录（这里用测试接口，不是真登录）
login_data = {"username": "test", "password": "123456"}
login_resp = login_session.post(
    "https://httpbin.org/post",
    data=login_data,
    headers={"User-Agent": "Mozilla/5.0"}
)
print(f"登录响应状态码: {login_resp.status_code}")

# 之后用同一个 session 去请求需要登录的页面
profile_resp = login_session.get(
    "https://httpbin.org/get",
    headers={"User-Agent": "Mozilla/5.0"}
)
print(f"访问个人页状态码: {profile_resp.status_code}")
print("登录后 session 中记录的 cookies:", login_session.cookies.get_dict())
