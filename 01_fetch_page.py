"""
第一课：发送 HTTP 请求，获取网页内容
"""

import requests

# 这是一个专门用来练习爬虫的网站
url = "http://quotes.toscrape.com/"

# 发送 GET 请求
response = requests.get(url)

# 状态码：200 表示成功
print(f"状态码: {response.status_code}")

# 打印网页的前 500 个字符，看看长什么样
print("=" * 50)
print("网页内容（前 500 字符）:")
print("=" * 50)
print(response.text[:500])
