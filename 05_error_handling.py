"""
第五课：异常处理 —— 让爬虫更健壮
现实的网站会超时、断连、返回空数据、结构变化
"""

import requests
from bs4 import BeautifulSoup
import time

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
}


def safe_get(url, retries=3):
    """带重试的安全请求函数"""
    for attempt in range(retries):
        try:
            # timeout 防止永远等下去
            response = requests.get(url, headers=headers, timeout=10)

            # 检查状态码
            if response.status_code == 200:
                return response
            elif response.status_code == 429:
                # 豆瓣/知乎等常用网站429 表示「你爬太快了」
                wait = 10 * (attempt + 1)
                print(f"  触发频率限制，等待 {wait} 秒后重试...")
                time.sleep(wait)
            elif response.status_code == 403:
                print("  被屏蔽了（403），可能需要换 Cookie 或 IP")
                return None
            else:
                print(f"  状态码异常: {response.status_code}")

        except requests.exceptions.Timeout:
            print(f"  超时（第 {attempt+1} 次尝试）")
        except requests.exceptions.ConnectionError:
            print(f"  连接断开（第 {attempt+1} 次尝试）")
        except Exception as e:
            print(f"  未知错误: {e}")

        if attempt < retries - 1:
            time.sleep(3)  # 重试前等 3 秒

    return None


def parse_movie(item):
    """安全提取单条电影信息，避免某字段缺失导致整个程序崩溃"""
    try:
        # 核心字段：缺了就跳过这条
        title_tag = item.select_one(".title")
        if not title_tag:
            return None

        rank = item.select_one(".pic em")
        rating = item.select_one(".rating_num")
        quote_tag = item.select_one(".inq")

        return {
            "rank": rank.text.strip() if rank else "?",
            "title": title_tag.text.strip(),
            "rating": rating.text.strip() if rating else "?",
            "quote": quote_tag.text.strip() if quote_tag else "",
        }
    except Exception as e:
        print(f"  解析一条数据时出错: {e}")
        return None


# === 主程序 ===
base_url = "https://movie.douban.com/top250"
all_movies = []

for page in range(10):
    url = f"{base_url}?start={page * 25}"
    print(f"\n第 {page+1} 页...")

    response = safe_get(url)
    if response is None:
        print("  请求失败，跳过该页")
        continue

    soup = BeautifulSoup(response.text, "lxml")
    items = soup.select(".item")

    if not items:
        print("  页面结构异常，未找到电影数据")
        continue

    for item in items:
        movie = parse_movie(item)
        if movie:
            all_movies.append(movie)

    print(f"  本页成功提取 {min(len(items), sum(1 for _ in items))} 条")
    time.sleep(1.5)

print(f"\n总结：成功爬取 {len(all_movies)} 条数据")

# 额外统计
ratings = [float(m["rating"]) for m in all_movies if m["rating"] != "?"]
if ratings:
    avg = sum(ratings) / len(ratings)
    print(f"平均评分: {avg:.2f}")
    print(f"最高分: {max(ratings)}，最低分: {min(ratings)}")
