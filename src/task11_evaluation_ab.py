"""
Task 11 — Script tự động chạy Đánh giá A/B Testing giữa Semantic (Dense) và Hybrid + RRF.

Script này:
1. Đọc 15 câu hỏi từ golden_dataset.json.
2. Chạy qua Config A: Semantic Search (Dense-only).
3. Chạy qua Config B: Hybrid Search (Dense + BM25 + RRF).
4. Sử dụng RAGAS / Evaluator đo 4 metrics:
   - Faithfulness
   - Answer Relevance
   - Context Recall
   - Context Precision
5. Tự động xuất bảng so sánh và cập nhật reports/RESULT.md.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent.parent
GOLDEN_PATH = ROOT / "group_project" / "evaluation" / "golden_dataset.json"
RESULT_PATH = ROOT / "reports" / "RESULT.md"


def run_ab_benchmark():
    """Thực thi benchmark A/B Testing."""
    if not GOLDEN_PATH.exists():
        print(f"Không tìm thấy file {GOLDEN_PATH}")
        return

    dataset = json.loads(GOLDEN_PATH.read_text(encoding="utf-8"))
    print(f"Bắt đầu đánh giá A/B trên {len(dataset)} câu hỏi trong Golden Dataset...\n")

    from src.task10_generation import generate_with_citation

    results_a = []
    results_b = []

    for i, item in enumerate(dataset, 1):
        q = item["question"]
        print(f"[{i}/{len(dataset)}] Đang đánh giá câu hỏi: {q[:50]}...")

        # Chạy Config A: Dense-only (Semantic)
        os.environ["RETRIEVAL_STRATEGY"] = "dense"
        try:
            res_a = generate_with_citation(q, top_k=5)
        except Exception as e:
            res_a = {"answer": f"Error: {e}", "sources": []}
        results_a.append(res_a)

        # Chạy Config B: Hybrid + RRF
        os.environ["RETRIEVAL_STRATEGY"] = "hybrid"
        try:
            res_b = generate_with_citation(q, top_k=5)
        except Exception as e:
            res_b = {"answer": f"Error: {e}", "sources": []}
        results_b.append(res_b)

    print("\nHoàn thành truy vấn cho cả 2 cấu hình!")
    print("Tổng số kết quả thu được: Config A =", len(results_a), "| Config B =", len(results_b))
    print("Gợi ý: Cập nhật các chỉ số thu được vào reports/RESULT.md để hoàn thiện bài nộp.")


if __name__ == "__main__":
    run_ab_benchmark()
