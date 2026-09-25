"""
Task 2 — Crawl bài viết/thông báo.

Hướng dẫn:
    1. Điền tối thiểu 5 URL công khai vào ARTICLE_URLS.
    2. Crawl từng URL bằng Crawl4AI.
    3. Lưu mỗi bài thành một JSON trong data/landing/news/.
    4. Giữ đủ url, title, date_crawled và content_markdown.

Cài browser trước khi chạy:
    python -m playwright install chromium
    
-> Dùng Firecrawl or bất cứ công cụ nào bạn quen    
"""

import asyncio
import json
from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"

ARTICLE_URLS = [
    "https://ctsv.uit.edu.vn/bai-viet/huong-dan-ve-qui-dinh-hoc-bong-khuyen-khich-hoc-tap-moi-tu-hk1-2026-2027",
    "https://ctsv.uit.edu.vn/bai-viet/quy-dinh-lien-quan-den-hoc-bong-sinh-vien",
    "https://ctsv.uit.edu.vn/bai-viet/danh-sach-du-kien-nhan-cac-loai-hoc-bong-tai-hk2-2025-2026",
    "https://ctsv.uit.edu.vn/bai-viet/thong-bao-trien-khai-hoc-bong-uit-global-tu-hoc-ky-1-nam-hoc-2026-2027",
    "https://ctsv.uit.edu.vn/bai-viet/hoc-phi-hoc-bong-mien-giam-hoc-phi-cac-che-do-chinh-sach-khac",
]


async def crawl_article(url: str) -> dict:
    """Crawl một bài viết từ URL và trích xuất metadata kèm markdown."""
    from datetime import datetime
    import requests
    from bs4 import BeautifulSoup
    import markdownify

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    resp = requests.get(url, headers=headers, timeout=20)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.content, "html.parser")

    # Trích xuất tiêu đề bài viết
    h1 = soup.find("h1")
    if h1 and h1.get_text(strip=True):
        title = h1.get_text(strip=True)
    elif soup.title and soup.title.get_text(strip=True):
        title = soup.title.get_text(strip=True)
    else:
        title = "Thông báo sinh viên"

    # Trích xuất nội dung chính
    content_el = (
        soup.find("div", class_="field-name-body")
        or soup.find("div", class_="node__content")
        or soup.find("article")
        or soup.find("div", class_="content")
        or soup.body
    )

    markdown_text = markdownify.markdownify(
        str(content_el),
        heading_style="ATX",
        strip=["script", "style", "nav", "footer"],
    ).strip()

    return {
        "url": url,
        "title": title,
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": markdown_text,
    }


async def crawl_all() -> None:
    """Crawl và lưu từng bài thành một file JSON."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    for index, url in enumerate(ARTICLE_URLS, 1):
        try:
            article = await crawl_article(url)
            output = DATA_DIR / f"article_{index:02d}.json"
            output.write_text(
                json.dumps(article, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            print(f"Saved: {output}")
        except Exception as error:
            print(f"Failed: {url} — {error}")


if __name__ == "__main__":
    asyncio.run(crawl_all())
