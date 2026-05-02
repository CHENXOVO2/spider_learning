"""
第六课：下载图片 —— 爬虫里最直观好玩的部分
目标：下载豆瓣 Top250 的电影海报
"""

import requests
from bs4 import BeautifulSoup
import os
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
}

# 创建保存图片的文件夹
os.makedirs("posters", exist_ok=True)

base_url = "https://movie.douban.com/top250"
downloaded = 0

for page in range(2):  # 先试 2 页
    url = f"{base_url}?start={page * 25}"
    print(f"\n第 {page+1} 页...")

    response = requests.get(url, headers=headers, timeout=10)
    soup = BeautifulSoup(response.text, "lxml")

    for item in soup.select(".item"):
        # 电影名（用来做文件名）
        title = item.select_one(".title").text.strip()
        # 图片 URL
        img_tag = item.select_one(".pic img")
        img_url = img_tag["src"]

        # 去掉文件名中的非法字符
        safe_title = title.replace(":", "：").replace("/", "／").replace("?", "？")
        filename = f"posters/{safe_title}.jpg"

        # 下载图片，保存到文件夹
        try:
            img_data = requests.get(img_url, headers=headers, timeout=10).content
            with open(filename, "wb") as f:  # wb = 二进制写入
                f.write(img_data)
            downloaded += 1
            print(f"  [OK] {title}")
        except Exception as e:
            print(f"  [FAIL] {title}: {e}")

    time.sleep(1)

print(f"\n完成！共下载 {downloaded} 张海报到 posters/ 文件夹")
