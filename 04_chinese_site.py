"""
第四课：爬中文网站 + 伪装浏览器 + 处理编码 + 输出到文件
目标：爬豆瓣电影 Top250 保存到 txt
"""

import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

base_url = "https://movie.douban.com/top250"
all_movies = []

for page in range(10):  # 豆瓣 Top250 共 10 页
    params = {"start": page * 25, "filter": ""}
    print(f"正在爬取第 {page+1} 页...")

    response = requests.get(base_url, headers=headers, params=params)
    soup = BeautifulSoup(response.text, "lxml")

    for item in soup.select(".item"):
        # 排名
        rank = item.select_one(".pic em").text
        # 电影名
        title = item.select_one(".title").text
        # 评分
        rating = item.select_one(".rating_num").text
        # 评语（可能没有）
        quote_tag = item.select_one(".inq")
        quote = quote_tag.text if quote_tag else ""
        # 链接
        link = item.select_one("a")["href"]

        all_movies.append({
            "rank": rank,
            "title": title,
            "rating": rating,
            "quote": quote,
            "link": link,
        })

    time.sleep(1)  # 每页间隔 1 秒，别把豆瓣爬挂了

# 写入文本文件，用 UTF-8 编码
with open("douban_top250.txt", "w", encoding="utf-8") as f:
    for m in all_movies:
        f.write(f"#{m['rank']}  {m['title']}  [{m['rating']}]\n")
        if m["quote"]:
            f.write(f"   → {m['quote']}\n")
        f.write(f"   {m['link']}\n\n")

print(f"\n完成！共爬取 {len(all_movies)} 部电影")
print("结果已保存到 douban_top250.txt，用记事本/WPS 打开看")
