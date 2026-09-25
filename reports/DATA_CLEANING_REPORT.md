# BÁO CÁO KỸ THUẬT: TẠI SAO PHẢI LÀM SẠCH DỮ LIỆU VÀ ĐÃ LÀM SẠCH NHƯ THẾ NÀO

- **Người thực hiện:** Đậu Quang Ý
- **MSSV:** 2A202602661
- **Nhóm:** K4-L3B-Day08-KhongBiet
- **Nhiệm vụ phụ trách:** Task 1 (Thu thập tài liệu quy chế), Task 2 (Crawl bài viết thông báo), Task 3 (Chuẩn hóa sang Markdown)
- **Chủ đề dữ liệu:** Quy chế đào tạo, học bổng & dịch vụ sinh viên Đại học

---

## I. TẠI SAO PHẢI LÀM SẠCH DỮ LIỆU TRONG RAG? (THE "WHY")

Trong kiến trúc **RAG (Retrieval-Augmented Generation)**, câu châm ngôn cốt lõi là **"Garbage In, Garbage Out"** — nếu chất lượng dữ liệu đầu vào không sạch và chuẩn hóa, toàn bộ các khâu tìm kiếm (Retrieval) và sinh câu trả lời (Generation) phía sau sẽ gặp lỗi nghiêm trọng.

Cụ thể, việc làm sạch dữ liệu giải quyết 5 bài toán sống còn sau:

### 1. Loại bỏ "nhiễu" (Noise) gây sai lệch công cụ tìm kiếm (Hybrid Search)
* **Vấn đề của dữ liệu thô từ Web:** Một trang web trường đại học chứa vô số thành phần phụ như thanh menu điều hướng (`<nav>`), chân trang (`<footer>`), banner quảng cáo, nút chia sẻ mạng xã hội, các đoạn script JavaScript và stylesheet CSS.
* **Tác động tiêu cực:**
  * **Với BM25 (Lexical Search):** Tần số xuất hiện của các từ khóa điều hướng (ví dụ: *"Trang chủ"*, *"Tin tức"*, *"Liên hệ"*, *"Tìm kiếm"*) rất cao, làm sai lệch trọng số TF-IDF và khiến BM25 trả về các đoạn văn bản rác thay vì nội dung câu trả lời thực tế.
  * **Với Dense Retrieval (Vector Search):** Khi embedding một đoạn văn bản có chứa code HTML hoặc menu, vector ngữ nghĩa (embedding vector) bị lệch hướng hoàn toàn so với ngữ cảnh thực sự của văn bản quy chế.

### 2. Bảo toàn cấu trúc ngữ nghĩa (Semantic Hierarchy) phục vụ cho Chunking
* Văn bản quy chế đào tạo và chính sách đại học có cấu trúc phân cấp rất chặt chẽ: **Chương $\rightarrow$ Điều $\rightarrow$ Khoản $\rightarrow$ Điểm**.
* Nếu chỉ trích xuất text thô dạng plain text không định dạng, các ranh giới này bị xóa nhòa. Khi sang **Task 4 (Chunking)**, bộ cắt văn bản (Text Splitter) sẽ rất dễ cắt đôi một câu hoặc cắt ngang giữa điều kiện và kết quả của một chính sách.
* Định dạng **Markdown** chuẩn hóa giữ nguyên các thẻ tiêu đề (`#`, `##`, `###`), danh sách liệt kê (`-`, `1. 2.`) và bảng biểu (`|---|`), giúp các thuật toán cắt đoạn (như `MarkdownHeaderTextSplitter` hoặc `RecursiveCharacterTextSplitter`) phân tách dữ liệu chính xác theo từng đơn vị ngữ nghĩa.

### 3. Tiết kiệm Token, chi phí API và tối ưu độ dài ngữ cảnh (Context Window)
* Mã nguồn HTML thô có thể dài gấp 5 đến 10 lần nội dung văn bản thực tế.
* Việc loại bỏ triệt để HTML boilerplate giúp:
  * Giảm chi phí tạo Vector Embedding trên toàn bộ corpus.
  * Giảm số lượng token gửi vào LLM (OpenAI / Gemini / Claude) trong prompt sinh câu trả lời.
  * Tránh làm cạn kiệt hoặc tràn cửa sổ ngữ cảnh (Context Window), cho phép đưa được nhiều đoạn ngữ cảnh hữu ích (top-k chunks) vào prompt hơn.

### 4. Hỗ trợ cơ chế Trích dẫn nguồn (Citation & Evidence Grounding)
* Một yêu cầu bắt buộc của bài lab ở Task 10 là chatbot phải trả lời kèm **trích dẫn nguồn (citation)** rõ ràng để chống ảo giác (hallucination).
* Để LLM có thể trích dẫn được, mỗi văn bản trong corpus cần phải được "đóng gói" sẵn thông tin xuất xứ: Tiêu đề bài viết (`Title`), Đường dẫn gốc (`Source URL`), và Thời điểm thu thập (`Date Crawled`).

### 5. Khắc phục vấn đề lỗi font tiếng Việt và tài liệu scan rỗng
* Các hệ thống trích xuất văn bản trên Windows thường mặc định dùng bảng mã nội bộ (`cp1252`/`charmap`), dễ gây lỗi vỡ font tiếng Việt có dấu.
* Nếu tải phải tài liệu scan dạng hình ảnh không có text layer, bộ parser sẽ trả về kết quả rỗng hoặc chỉ vài ký tự rác, dẫn đến pipeline retrieval thất bại hoàn toàn.

---

## II. ĐÃ LÀM SẠCH DỮ LIỆU NHƯ THẾ NÀO? (THE "HOW")

Hệ thống đã triển khai quy trình làm sạch dữ liệu tự động, khép kín qua 2 pipeline chuyên biệt:

```
[Nguồn Web HTML] ──(BeautifulSoup + markdownify)──> [JSON Landing] ──(Header Metadata)──> [Markdown Standardized]
[Nguồn PDF Gốc]  ──(Lọc Digital Text Layer)    ──> [PDF Landing]  ──(MarkItDown Engine)──> [Markdown Standardized]
```

### 1. Quy trình làm sạch bài viết Web / Thông báo sinh viên (`Task 2 & 3`)

Quy trình được thực hiện qua các bước tại [`src/task2_crawl_news.py`](file:///c:/Users/iDEAPAD/Downloads/Day8/K4-L3B-Day08-KhongBiet/src/task2_crawl_news.py) và [`src/task3_convert_markdown.py`](file:///c:/Users/iDEAPAD/Downloads/Day8/K4-L3B-Day08-KhongBiet/src/task3_convert_markdown.py):

* **Bước 1 — Bóc tách chính xác vùng nội dung chính (Container Filtering):**
  Thay vì lấy toàn bộ thẻ `<body>`, script dùng BeautifulSoup để tìm đúng thẻ container chứa nội dung bài viết:
  ```python
  content_el = (
      soup.find("div", class_="field-name-body")
      or soup.find("div", class_="node__content")
      or soup.find("article")
  )
  ```
  $\rightarrow$ Tự động triệt tiêu 100% các thành phần menu, thanh bên (sidebar), quảng cáo, chân trang.

* **Bước 2 — Loại bỏ thẻ độc hại và rác mã nguồn (Tag Stripping):**
  Sử dụng `markdownify` với bộ lọc loại bỏ toàn bộ thẻ kỹ thuật:
  ```python
  markdown_text = markdownify.markdownify(
      str(content_el),
      heading_style="ATX",
      strip=["script", "style", "nav", "footer"]
  ).strip()
  ```

* **Bước 3 — Chuẩn hóa Header Metadata phục vụ Citation:**
  Mỗi bài viết khi chuyển đổi sang `data/standardized/news/*.md` đều được chèn cấu trúc header thống nhất:
  ```markdown
  # {Tiêu đề bài viết}

  **Source:** {URL nguồn bài viết}

  **Crawled:** {Thời điểm crawl chuẩn ISO 8601}

  ---

  {Nội dung bài viết đã làm sạch}
  ```

### 2. Quy trình làm sạch và chuyển đổi tài liệu Quy chế PDF (`Task 1 & 3`)

Quy trình được thực hiện tại [`src/task1_collect_legal_docs.py`](file:///c:/Users/iDEAPAD/Downloads/Day8/K4-L3B-Day08-KhongBiet/src/task1_collect_legal_docs.py) và [`src/task3_convert_markdown.py`](file:///c:/Users/iDEAPAD/Downloads/Day8/K4-L3B-Day08-KhongBiet/src/task3_convert_markdown.py):

* **Bước 1 — Sàng lọc chất lượng văn bản gốc (Digital PDF vs Scanned PDF):**
  * Trong quá trình thử nghiệm, phát hiện một số file thông báo học bổng tải về là bản scan dạng hình ảnh (chỉ có ảnh chụp văn bản, không có text layer), khiến công cụ trích xuất chỉ đọc được 1 - 4 ký tự.
  * **Giải pháp:** Sàng lọc và thay thế bằng các văn bản quy chế chính thức có lớp số hóa nguyên bản (Digital Text Layer) của trường Đại học Công nghệ Thông tin (ĐHQG-HCM), đảm bảo mọi file đều có nội dung văn bản đầy đủ và sắc nét.

* **Bước 2 — Chuyển đổi cấu trúc bằng bộ công cụ `MarkItDown`:**
  * Tích hợp `MarkItDown` cùng các engine xử lý PDF chuyên sâu (`pdfminer-six`, `pdfplumber`).
  * Tự động trích xuất các tiêu đề, đề mục chương điều và chuyển đổi các bảng biểu quy chế (thang điểm rèn luyện, khung học phí, điều kiện học bổng) thành định dạng bảng Markdown `| Cột 1 | Cột 2 |`.

* **Bước 3 — Chuẩn hóa mã hóa ký tự (UTF-8 Enforcing):**
  * Toàn bộ thao tác ghi file `*.md` đều gán cứng `encoding="utf-8"`, loại bỏ nguy cơ lỗi mã hóa ký tự trên các hệ điều hành khác nhau.

---

## III. KẾT QUẢ ĐẠT ĐƯỢC VÀ BẰNG CHỨNG THỰC NGHIỆM

### 1. Thống kê dữ liệu sau khi làm sạch

| STT | Tên file đã chuẩn hóa | Loại nguồn | Dung lượng / Độ dài ký tự | Đánh giá chất lượng sau làm sạch |
|---|---|---|---|---|
| 1 | `quy_che_dao_tao_dai_hoc.md` | Pháp lý / Quy chế | 65.290 ký tự | Giữ nguyên 27 trang quy chế tín chỉ, cấu trúc Chương/Điều chuẩn |
| 2 | `quy_che_an_toan_thong_tin.md` | Pháp lý / Quy chế | 37.063 ký tự | Toàn bộ 16 trang quy chế bảo đảm ATTT sinh viên |
| 3 | `quy_dinh_danh_gia_ren_luyen.md` | Pháp lý / Quy chế | 33.541 ký tự | Giữ đầy đủ thang bảng điểm rèn luyện và tiêu chí đánh giá |
| 4 | `quy_che_dao_tao_ngoai_ngu.md` | Pháp lý / Quy chế | 28.609 ký tự | Quy định chuẩn đầu ra, miễn giảm chứng chỉ ngoại ngữ |
| 5 | `article_01.md` | Tin tức / Thông báo | 4.714 ký tự | Quy định học bổng KKHT mới, có đủ Header & Source |
| 6 | `article_02.md` | Tin tức / Thông báo | 1.974 ký tự | Quy định học bổng sinh viên, sạch rác HTML |
| 7 | `article_03.md` | Tin tức / Thông báo | 4.652 ký tự | Danh sách & hướng dẫn nhận học bổng |
| 8 | `article_04.md` | Tin tức / Thông báo | 6.318 ký tự | Học bổng ngoại ngữ UIT Global |
| 9 | `article_05.md` | Tin tức / Thông báo | 9.001 ký tự | Tổng hợp học phí, miễn giảm học phí và chế độ chính sách |

### 2. Kết quả kiểm thử tự động (Acceptance Tests)

Khi chạy kiểm thử nghiệm thu với pytest:
```bash
pytest tests/test_acceptance.py -k "test_corpus or test_standardized" -v
```

Kết quả:
```text
tests/test_acceptance.py::test_corpus_has_required_legal_documents PASSED [ 33%]
tests/test_acceptance.py::test_corpus_has_required_news_with_metadata PASSED [ 66%]
tests/test_acceptance.py::test_standardized_output_covers_both_source_types PASSED [100%]

======================= 3 passed, 2 deselected in 0.30s =======================
```

* **100% tài liệu pháp lý** đều vượt xa tiêu chuẩn $> 1$ KB.
* **100% bài viết tin tức** đều có đầy đủ 4 trường metadata chuẩn.
* **100% file Markdown** đều đạt độ dài từ 1.900 đến 65.200 ký tự (vượt xa mức tối thiểu 200 ký tự của đề bài).

---

## IV. KẾT LUẬN

Việc làm sạch và chuẩn hóa dữ liệu ở Task 1, 2, 3 đã xây dựng một nền móng ngữ liệu (corpus) chất lượng cao cho nhóm. Dữ liệu sau khi làm sạch không còn rác HTML, bảo toàn toàn vẹn phân cấp điều khoản và có sẵn metadata trích dẫn nguồn, giúp các bạn thành viên phụ trách các công đoạn sau (Task 4: Chunking, Task 5-7: Hybrid Search, Task 8-10: Generation & UI) đạt độ chính xác tối đa và không gặp lỗi vỡ cấu trúc.
