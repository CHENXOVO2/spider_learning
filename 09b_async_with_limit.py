"""
第09课(实战)：异步爬虫 — 带限速的并发爬取 + BeautifulSoup解析
并发爬取时一定要控制速率，避免被服务器封IP
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
import time
from typing import List, Dict

# asyncio 版的重试装饰器
async def fetch_with_retry(
    session: aiohttp.ClientSession,
    url: str,
    max_retries: int = 3,
) -> str:
    """带重试的异步请求"""
    for attempt in range(1, max_retries + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=15)) as resp:
                if resp.status == 200:
                    return await resp.text()
                elif resp.status == 429:  # Too Many Requests
                    wait = min(2 ** attempt, 10)
                    print(f"  触发限速，等待 {wait}s 后重试...")
                    await asyncio.sleep(wait)
                else:
                    print(f"  状态码 {resp.status}，重试 {attempt}/{max_retries}")
        except Exception as e:
            print(f"  请求失败: {e}，重试 {attempt}/{max_retries}")
            if attempt < max_retries:
                await asyncio.sleep(2 ** attempt)
    return ""


async def crawl_pages(
    base_url: str,
    total_pages: int,
    concurrency: int = 3,
    delay: float = 1.0,
) -> List[Dict]:
    """
    并发爬取多页，同时控制并发数和请求间隔

    Args:
        base_url: URL模板，用 {page} 占位
        total_pages: 总页数
        concurrency: 最大并发数
        delay: 每个请求后的最小间隔(秒)
    """
    semaphore = asyncio.Semaphore(concurrency)
    results = []

    # 信号量 + 延迟 = 精细的速率控制
    async def rate_limited_fetch(session: aiohttp.ClientSession, page: int):
        url = base_url.format(page=page)
        async with semaphore:  # 限制并发数
            print(f"→ 正在抓取第 {page} 页: {url}")
            html = await fetch_with_retry(session, url)
            if html:
                # 用 BeautifulSoup 解析（注意：BeautifulSoup 是同步的，
                # 但解析速度远快于网络IO，在异步中直接调没问题）
                soup = BeautifulSoup(html, "html.parser")
                # 提取页面文本长度作为示例
                text_len = len(soup.get_text(strip=True))
                results.append({"page": page, "url": url, "size": text_len})
                print(f"  ✓ 第 {page} 页完成，文本长度: {text_len}")
            else:
                results.append({"page": page, "url": url, "size": 0})
                print(f"  ✗ 第 {page} 页失败")

            await asyncio.sleep(delay)  # 请求间隔

    async with aiohttp.ClientSession() as session:
        tasks = [rate_limited_fetch(session, page) for page in range(1, total_pages + 1)]
        await asyncio.gather(*tasks)

    return results


def main():
    print("=" * 50)
    print("异步爬虫实战 — 限速并发")
    print("=" * 50)
    print("并发数: 3 | 请求间隔: 1s | 总页数: 5")
    print("-" * 50)

    # 用 httpbin 模拟分页请求（实际项目中替换为目标网站）
    base_url = "https://httpbin.org/anything?page={page}"

    start = time.perf_counter()
    results = asyncio.run(crawl_pages(base_url, total_pages=5, concurrency=3, delay=0.5))
    elapsed = time.perf_counter() - start

    print("-" * 50)
    print(f"完成! 耗时 {elapsed:.2f} 秒")
    print(f"成功: {sum(1 for r in results if r['size'] > 0)} / {len(results)}")
    print(f"平均每页耗时: {elapsed / len(results):.2f} 秒")

    # 对比：如果同步爬取5页（每页1秒），需要约5秒
    print(f"对比同步: 同样任务同步执行约需 {len(results)} 秒以上")


if __name__ == "__main__":
    main()
