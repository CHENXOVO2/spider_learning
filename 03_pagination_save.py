"""
第三课：翻页爬取 + 保存到 CSV 文件
"""

import requests
from bs4 import BeautifulSoup
import csv
import time


def scrape_page(url):
    """爬取单页的名言，返回 (名言列表, 是否有下一页)"""
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "lxml")

    quotes = []
    for q in soup.find_all("div", class_="quote"):
        text = q.find("span", class_="text").text
        author = q.find("small", class_="author").text
        tags = ", ".join([t.text for t in q.find_all("a", class_="tag")])
        quotes.append({"text": text, "author": author, "tags": tags})

    # 检查是否有下一页
    next_btn = soup.find("li", class_="next")
    has_next = next_btn is not None

    return quotes, has_next


# 爬取所有页
base_url = "http://quotes.toscrape.com"
page_url = "/page/1/"
all_quotes = []
page_num = 1

print("开始爬取...")

while page_url:
    url = base_url + page_url
    print(f"  正在爬取第 {page_num} 页...")

    quotes, has_next = scrape_page(url)
    all_quotes.extend(quotes)

    if has_next:
        page_num += 1
        page_url = f"/page/{page_num}/"
        time.sleep(1)  # 礼貌爬取，不要请求太快
    else:
        page_url = None

print(f"\n共爬取 {len(all_quotes)} 条名言，保存到文件...")

# 保存为 CSV 文件（可以用 Excel/WPS 打开）
with open("quotes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=["text", "author", "tags"])
    writer.writeheader()
    writer.writerows(all_quotes)

print("完成！文件已保存为 quotes.csv")
