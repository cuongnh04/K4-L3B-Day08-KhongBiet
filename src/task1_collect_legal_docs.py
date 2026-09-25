"""
Task 1 — Thu thập tài liệu chính sách/quy định.

Hướng dẫn:
    1. Chọn chủ đề của nhóm.
    2. Tìm tối thiểu 3 tài liệu PDF/DOCX từ nguồn công khai.
    3. Lưu file gốc vào data/landing/legal/.
    4. Đặt tên không dấu và thể hiện đúng nội dung.

Ví dụ tài liệu: học phí, học bổng, ký túc xá, quy trình đăng ký.
Nếu website chặn crawler, hãy chọn nguồn công khai khác; không vượt WAF.
"""

from pathlib import Path


DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"

LEGAL_SOURCES = {
    "quy_che_dao_tao_dai_hoc.pdf": "https://daa.uit.edu.vn/sites/daa/files/202309/790-qd-dhcntt_28-9-22_quy_che_dao_tao.pdf",
    "quy_dinh_danh_gia_ren_luyen.pdf": "https://ctsv.uit.edu.vn/sites/default/files/202005/139_qd.pdf",
    "quy_che_an_toan_thong_tin.pdf": "https://www.uit.edu.vn/media/quy_che_attt_uit_final_b4bdd2c523.pdf",
    "quy_che_dao_tao_ngoai_ngu.pdf": "https://daa.uit.edu.vn/sites/daa/files/202608/956-qd-dhcntt_10-8-2026_quy_che_dao_tao_ngoai_ngu_tu_khoa_2026_0.pdf",
}


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Ready: {DATA_DIR}")


def download_documents() -> None:
    """Tải ít nhất 3 PDF/DOCX từ nguồn công khai."""
    import requests
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    setup_directory()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for filename, url in LEGAL_SOURCES.items():
        dest = DATA_DIR / filename
        print(f"Downloading {filename} from {url}...")
        try:
            resp = requests.get(url, headers=headers, timeout=60, verify=False)
            resp.raise_for_status()
            dest.write_bytes(resp.content)
            size_kb = len(resp.content) / 1024
            print(f"Saved: {dest} ({size_kb:.1f} KB)")
        except Exception as exc:
            print(f"Failed to download {filename}: {exc}")


if __name__ == "__main__":
    setup_directory()
    download_documents()
