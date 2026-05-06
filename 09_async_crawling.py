"""
第09课：异步爬虫 — 用 aiohttp 并发请求
比 requests 快数倍到数十倍，适合大批量URL采集
"""

import asyncio
import aiohttp
import time
from typing import List, Dict

# 示例：并发爬取多个页面
URLS = [
    "https://httpbin.org/delay/1",  # 会延迟1秒返回
    "https://httpbin.org/delay/2",
    "https://httpbin.org/delay/1",
    "https://httpbin.org/delay/3",
    "https://httpbin.org/delay/2",
    "https://httpbin.org/get?page=1",
    "https://httpbin.org/get?page=2",
    "https://httpbin.org/get?page=3",
]


async def fetch_one(session: aiohttp.ClientSession, url: str) -> Dict:
    """请求单个页面"""
    try:
        async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            print(f"  ✓ {url} -> 状态码 {resp.status}")
            return {"url": url, "status": resp.status, "data": data}
    except Exception as e:
        print(f"  ✗ {url} -> 错误: {e}")
        return {"url": url, "status": 0, "error": str(e)}


async def crawl_all(urls: List[str]) -> List[Dict]:
    """并发爬取所有URL"""
    # 连接池复用，默认限制100个并发连接
    connector = aiohttp.TCPConnector(limit=10)  # 限制最多10个并发
    async with aiohttp.ClientSession(connector=connector) as session:
        # 创建所有任务并发执行
        tasks = [fetch_one(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return results


def main():
    print("=" * 50)
    print("异步爬虫演示 — 并发请求")
    print("=" * 50)

    start = time.perf_counter()
    results = asyncio.run(crawl_all(URLS))
    elapsed = time.perf_counter() - start

    print(f"\n完成! 共爬取 {len(results)} 个URL，耗时 {elapsed:.2f} 秒")
    print(f"成功: {sum(1 for r in results if r['status'] == 200)}")
    print(f"失败: {sum(1 for r in results if r['status'] != 200)}")


if __name__ == "__main__":
    main()
