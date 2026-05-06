"""
第10课：爬虫数据的清洗与存储 — SQLite + CSV + 数据去重
爬虫拿到的数据往往是脏的，清洗后再存储才是可用的数据
"""

import sqlite3
import csv
import re
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent / "crawled_data.db"
CSV_PATH = Path(__file__).parent / "crawled_data.csv"


# ─── 1. 数据库初始化 ─────────────────────────────────
def init_db():
    """创建数据库表，带唯一约束防重复"""
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,           -- URL唯一，避免重复
            title TEXT NOT NULL,
            author TEXT DEFAULT '',
            content_length INTEGER DEFAULT 0,
            tags TEXT DEFAULT '',
            crawled_at TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 建索引加速查询
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_articles_url
        ON articles(url)
    """)

    conn.commit()
    return conn


# ─── 2. 数据清洗函数 ─────────────────────────────────
def clean_title(raw_title: str) -> str:
    """清洗标题：去空格、去特殊字符"""
    if not raw_title:
        return "未命名"
    # 替换多个空白为单个空格
    title = re.sub(r'\s+', ' ', raw_title.strip())
    # 去掉不可见字符
    title = ''.join(c for c in title if c.isprintable() or c in ' ')
    return title[:200]  # 截断过长的标题


def clean_tags(raw_tags: Optional[str]) -> str:
    """清洗标签：统一小写、去重"""
    if not raw_tags:
        return ""
    # 按逗号/空格分割
    parts = re.split(r'[,，、\s]+', raw_tags)
    # 去空、去重、小写
    cleaned = list(dict.fromkeys(p.strip().lower() for p in parts if p.strip()))
    return ','.join(cleaned)


def is_duplicate_url(conn: sqlite3.Connection, url: str) -> bool:
    """检查URL是否已存在"""
    cursor = conn.execute("SELECT COUNT(*) FROM articles WHERE url = ?", (url,))
    return cursor.fetchone()[0] > 0


# ─── 3. 存储函数 ────────────────────────────────────
def save_to_db(conn: sqlite3.Connection, articles: List[Dict]) -> tuple:
    """
    批量存储到SQLite，自动去重
    返回: (新增数, 跳过数)
    """
    added = 0
    skipped = 0

    for article in articles:
        try:
            conn.execute("""
                INSERT OR IGNORE INTO articles
                (url, title, author, content_length, tags, crawled_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                article["url"],
                clean_title(article.get("title", "")),
                article.get("author", ""),
                article.get("content_length", 0),
                clean_tags(article.get("tags", "")),
                datetime.now().isoformat(),
            ))
            # rowcount = 1 表示插入成功，0 表示因 UNIQUE 冲突跳过
            if conn.cursor().rowcount > 0:
                added += 1
            else:
                skipped += 1
        except Exception as e:
            print(f"  存储失败 [{article.get('url', 'unknown')}]: {e}")
            skipped += 1

    conn.commit()
    return added, skipped


def export_to_csv(conn: sqlite3.Connection, csv_path: str = str(CSV_PATH)):
    """导出数据库到CSV文件"""
    cursor = conn.execute("SELECT url, title, author, content_length, tags, crawled_at FROM articles")
    rows = cursor.fetchall()

    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["URL", "标题", "作者", "内容长度", "标签", "抓取时间"])
        writer.writerows(rows)

    print(f"  已导出 {len(rows)} 条数据到 {csv_path}")
    return len(rows)


# ─── 4. 演示 ─────────────────────────────────────────
def main():
    print("=" * 50)
    print("第10课：数据清洗与存储")
    print("=" * 50)

    # 模拟从爬虫抓来的原始数据（包含脏数据）
    raw_data = [
        {"url": "https://example.com/article/1", "title": "  Python爬虫  入门教程  ", "author": "Alice", "content_length": 3200, "tags": "Python,爬虫,入门"},
        {"url": "https://example.com/article/2", "title": "异步编程实战\n指南", "author": "Bob", "content_length": 5100, "tags": "异步,Python, 实战 "},
        {"url": "https://example.com/article/1", "title": "重复的URL", "author": "Alice", "content_length": 3200, "tags": ""},
        {"url": "https://example.com/article/3", "title": "  HTTP协议详解  ", "author": "Charlie", "content_length": 7800, "tags": "HTTP,网络,协议,网络"},
        {"url": "https://example.com/article/4", "title": "", "author": "David", "content_length": 0, "tags": None},
    ]

    print(f"\n原始数据: {len(raw_data)} 条（含1条重复、1条空标题）\n")

    # 清洗演示
    print("--- 清洗效果预览 ---")
    for item in raw_data:
        title_clean = clean_title(item.get("title", ""))
        tags_clean = clean_tags(item.get("tags"))
        print(f"  标题: {repr(item.get('title',''))} -> {repr(title_clean)}")
        if item.get("tags"):
            print(f"  标签: {repr(item.get('tags',''))} -> {repr(tags_clean)}")

    # 存储演示
    print("\n--- 存储到 SQLite ---")
    conn = init_db()
    added, skipped = save_to_db(conn, raw_data)
    print(f"  新增: {added} 条 | 跳过(重复/错误): {skipped} 条")

    # 再插入一次相同数据，查看去重效果
    added2, skipped2 = save_to_db(conn, raw_data)
    print(f"  再次插入: 新增 {added2} 条 | 跳过 {skipped2} 条 (全部跳过=去重成功)")

    # 查询验证
    cursor = conn.execute("SELECT COUNT(*) FROM articles")
    total = cursor.fetchone()[0]
    print(f"\n  数据库中总记录数: {total}")

    cursor = conn.execute("SELECT url, title, tags FROM articles")
    print("\n--- 数据库内容 ---")
    for row in cursor.fetchall():
        print(f"  {row[0]:45s} | {row[1]:20s} | {row[2]}")

    # 导出CSV
    print("\n--- 导出到 CSV ---")
    export_to_csv(conn)

    # 清理
    conn.close()
    print("\n提示: 数据库文件保存在", DB_PATH)


if __name__ == "__main__":
    main()
