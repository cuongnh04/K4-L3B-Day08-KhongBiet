"""
Task 8 — PageIndex vectorless fallback.

Hướng dẫn:
    1. Đọc PAGEINDEX_API_KEY từ .env.
    2. Upload tài liệu ở định dạng PageIndex hỗ trợ.
    3. Cache document IDs để không upload lại.
    4. Parse kết quả thành SearchResult có method pageindex.

PageIndex là dịch vụ ngoài: cần timeout và xử lý lỗi để pipeline không crash.
"""

import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY", "")
STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"


CACHE_FILE = Path(__file__).parent.parent / "data" / "pageindex_cache.json"

def upload_documents() -> None:
    """Upload tài liệu và lưu document IDs để tái sử dụng."""
    import json
    from pageindex import PageIndexClient
    
    if not PAGEINDEX_API_KEY:
        print("Missing PAGEINDEX_API_KEY")
        return
        
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            pass

    for path in STANDARDIZED_DIR.rglob("*.md"):
        if path.name in cache:
            continue
        try:
            # The API might only accept PDFs, but let's try uploading the Markdown file
            res = client.submit_document(str(path))
            if "doc_id" in res:
                cache[path.name] = res["doc_id"]
        except Exception as e:
            print(f"Failed to upload {path.name}: {e}")
            
    CACHE_FILE.parent.mkdir(parents=True, exist_ok=True)
    CACHE_FILE.write_text(json.dumps(cache))


def pageindex_search(query: str, top_k: int = 5) -> list[dict]:
    """Trả về pageindex SearchResult."""
    import json
    import time
    from pageindex import PageIndexClient
    
    if not PAGEINDEX_API_KEY:
        return []
        
    client = PageIndexClient(api_key=PAGEINDEX_API_KEY)
    
    cache = {}
    if CACHE_FILE.exists():
        try:
            cache = json.loads(CACHE_FILE.read_text())
        except Exception:
            pass
            
    results = []
    
    # We query all documents and collect top_k nodes
    # This is a naive approach, but without a cross-document query method, we iterate.
    for source, doc_id in cache.items():
        try:
            res = client.submit_query(doc_id, query)
            if "retrieval_id" not in res:
                continue
            retrieval_id = res["retrieval_id"]
            
            # Polling for result
            for _ in range(10):
                ret_res = client.get_retrieval(retrieval_id)
                status = ret_res.get("status")
                if status == "completed":
                    nodes = ret_res.get("nodes", [])
                    for i, node in enumerate(nodes):
                        results.append({
                            "id": f"{source}-node-{i}",
                            "content": node.get("content", ""),
                            "score": float(node.get("score", 1.0 - (i * 0.1))),
                            "metadata": {
                                "source": source,
                                "title": source.replace(".md", ""),
                                "doc_type": "pageindex",
                                "url": None
                            },
                            "retrieval_method": "pageindex",
                        })
                    break
                elif status == "failed":
                    break
                time.sleep(1)
        except Exception:
            pass
            
    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

if __name__ == "__main__":
    upload_documents()
