"""
第二课：用 BeautifulSoup 解析 HTML，提取名言
"""

import requests
from bs4 import BeautifulSoup

url = "http://quotes.toscrape.com/"
response = requests.get(url)

# 把网页文本交给 BeautifulSoup 解析
soup = BeautifulSoup(response.text, "lxml")

# 找到所有名言（每个名言在一个 <div class="quote"> 里）
quotes = soup.find_all("div", class_="quote")

print(f"本页共有 {len(quotes)} 条名言\n")

# 遍历每条名言，提取文本、作者、标签
for i, quote in enumerate(quotes, 1):
    text = quote.find("span", class_="text").text
    author = quote.find("small", class_="author").text
    tags = [tag.text for tag in quote.find_all("a", class_="tag")]

    print(f"{i}. 「{text}」")
    print(f"   作者: {author}")
    print(f"   标签: {', '.join(tags)}")
    print()
