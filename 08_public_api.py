"""
第八课：使用公开 API —— 比爬 HTML 更高效的方式
很多网站有隐藏的 JSON 接口，直接返回干净数据
"""

import requests

# ====== 1. 天气 API（无需 key）======
print("=== 当前天气 ===")
resp = requests.get("https://wttr.in/Beijing?format=j1", timeout=10)
weather = resp.json()  # .json() 直接把 JSON 字符串变成 Python 字典
#输出
current = weather["current_condition"][0]
print(f"  城市: {weather['nearest_area'][0]['areaName'][0]['value']}")
print(f"  温度: {current['temp_C']}°C")
print(f"  天气: {current['weatherDesc'][0]['value']}")
print(f"  湿度: {current['humidity']}%")

# ====== 2. GitHub 用户信息 API ======
print("\n=== GitHub 用户信息 ===")
resp = requests.get("https://api.github.com/users/torvalds", timeout=10)
user = resp.json()

print(f"  用户名: {user['login']}")
print(f"  昵称: {user['name']}")
print(f"  仓库数: {user['public_repos']}")
print(f"  粉丝: {user['followers']}")
print(f"  主页: {user['html_url']}")

# ====== 3. 获取 GitHub 仓库列表 ======
print("\n=== 最新公开仓库 ===")
resp = requests.get(
    "https://api.github.com/search/repositories?q=python&sort=stars&per_page=5",
    timeout=10,
    headers={"User-Agent": "Mozilla/5.0"}
)
data = resp.json()

for i, repo in enumerate(data["items"], 1):
    print(f"  {i}. {repo['full_name']}")
    print(f"     Stars: {repo['stargazers_count']}")
    print(f"     {repo['description'] or '（无描述）'}")
    print()

# ====== JSON 和 字典的关系 ======
print("=== JSON 怎么用？===")
# API 返回的是 JSON 字符串，用 .json() 转成 Python 字典/列表
# JSON 对象 → dict（花括号）
# JSON 数组 → list（方括号）
# 字符串 → str
# 数字 → int/float

sample = {"name": "小明", "scores": [90, 85, 92]}
import json
json_str = json.dumps(sample, ensure_ascii=False)
print(f"Python dict -> JSON:\n  {json_str}")
print(f"JSON -> Python dict:\n  {json.loads(json_str)}")
