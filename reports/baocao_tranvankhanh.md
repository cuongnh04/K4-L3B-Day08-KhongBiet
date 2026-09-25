# Individual contribution report

## Thông tin

- **Họ và tên:** Trần Văn Khánh
- **Vai trò:** Thành viên 2 (Indexing & Retrieval Specialist)
- **Mã học viên:** (Đang cập nhật)
- **Nhóm:** (Đang cập nhật)
- **Repository/branch:** main

## Phần việc đã thực hiện

| Module/deliverable | Việc tôi trực tiếp làm | File/commit/PR | Trạng thái |
|---|---|---|---|
| **Task 4: Chunking & Indexing** | Cài đặt `RecursiveCharacterTextSplitter` và `MarkdownHeaderTextSplitter`, chia văn bản thành các chunk. Dùng `google-genai` sinh embeddings qua Cloud model `gemini-embedding-2` và lưu dữ liệu vào `ChromaDB` (Persistent). | `src/task4_chunking_indexing.py` | Done |
| **Task 5: Semantic Search** | Truy vấn ChromaDB bằng cosine distance (chuyển đổi thành similarity score) để thực hiện Dense Retrieval. | `src/task5_semantic_search.py` | Done |
| **Task 6: Lexical Search** | Tokenize corpus và sử dụng `rank_bm25` (thuật toán `BM25Plus`) để tìm kiếm toàn văn chính xác theo từ khóa (Sparse Retrieval). | `src/task6_lexical_search.py` | Done |
| **Task 7: Reranking (RRF)** | Cài đặt thuật toán Reciprocal Rank Fusion (RRF) để gộp xếp hạng từ Dense và Sparse, công thức $\sum \frac{1}{k + rank}$ (với $k=60$). | `src/task7_reranking.py` | Done |
| **Task 8: PageIndex Fallback** | Viết fallback tích hợp API của `pageindex`, xử lý cache document_id và bẫy lỗi để pipeline không bị crash khi external service gặp sự cố. | `src/task8_pageindex_vectorless.py` | Done |
| **Task 9: Retrieval Pipeline** | Ghép nối toàn bộ luồng Hybrid search. Định tuyến: Nếu `best_dense_score < SCORE_THRESHOLD (0.3)`, kích hoạt fallback PageIndex; nếu không, trả về RRF Hybrid. | `src/task9_retrieval_pipeline.py` | Done |

Dưới đây là chi tiết các Task tôi đã trực tiếp đảm nhiệm (từ Task 4 đến Task 9). Với vai trò xây dựng cốt lõi của Retrieval Pipeline, tôi chú trọng tính module hóa và sự ổn định của hệ thống.

### Task 4: Chunking & Indexing (`src/task4_chunking_indexing.py`)
- **Thực hiện ra sao:** Đọc các file `.md`. Vì đề tài là "Quy chế đào tạo & Học bổng" mang tính cấu trúc cao, tôi sử dụng `MarkdownHeaderTextSplitter` để tách văn bản theo các thẻ tiêu đề (Header 1, 2, 3 tương ứng với Chương, Mục, Điều). Sau đó ghép tiêu đề vào ngữ cảnh (context) và dùng tiếp `RecursiveCharacterTextSplitter` cắt phần thân nhỏ hơn với `chunk_size = 500`. Cuối cùng, nhúng dữ liệu (embed) bằng model cloud **`gemini-embedding-2`** (sử dụng SDK `google-genai` với `EMBEDDING_DIM = 768`) và lưu vào ChromaDB.
- **Tại sao lại làm vậy:** 
  - Với tài liệu hành chính quy chế (như Nội quy đại học), một "Khoản 2" đứng lẻ loi sẽ vô nghĩa nếu bị cắt lìa khỏi "Điều 5" phía trên. Việc dùng `MarkdownHeaderTextSplitter` và nối thẻ header (`Header 2: Điều 5`) vào từng chunk giúp bảo tồn **ngữ cảnh pháp lý**, tránh model tìm sai quy chế. Kích thước 500 ký tự với overlap 50 ký tự đảm bảo lọt vừa ngữ cảnh.
  - Chuyển từ model local sang model Cloud `gemini-embedding-2` giúp bắt ngữ nghĩa vượt trội hơn rất nhiều đối với các ngữ cảnh khó và tiết kiệm đáng kể tài nguyên CPU/RAM tại môi trường local. Trả về vector 768 chiều nhỏ gọn nhưng vô cùng chính xác.

### Task 5: Semantic Search (`src/task5_semantic_search.py`)
- **Thực hiện ra sao:** Nhận câu query, chạy qua chung hàm embedding của Task 4 để lấy query_vector. Truy vấn ChromaDB để lấy ra `top_k` chunk giống nhất.
- **Tại sao lại làm vậy:** Semantic Search tìm kiếm theo "ý nghĩa" thay vì so khớp từ khóa. ChromaDB dùng phương pháp khoảng cách `cosine` nên tôi đổi điểm từ `distance` sang `similarity` (bằng `1.0 - distance`) để map chuẩn xác vào `SearchResult` contract. Điều này giúp các hàm đằng sau dễ dàng chuẩn hóa và so sánh.

### Task 6: Lexical Search (`src/task6_lexical_search.py`)
- **Thực hiện ra sao:** Tách từ (tokenize) câu truy vấn và kho tài liệu theo dấu cách (whitespace), đưa vào thuật toán `BM25Plus` (sử dụng thư viện `rank_bm25`) để sinh ra điểm số. 
- **Tại sao lại làm vậy:** Semantic Search cực kỳ kém ở các truy vấn chứa mã tài liệu, số hiệu (ví dụ: QĐ-123) hoặc tên người cụ thể. Thuật toán BM25 bù đắp lại điểm yếu này bằng việc đếm tần suất xuất hiện chính xác của từ khóa. Tôi dùng `BM25Plus` thay vì Okapi để xử lý triệt để lỗi tính IDF bằng 0 ở các corpus nhỏ, giữ cho kết quả xếp hạng luôn có sự chênh lệch rõ ràng.

### Task 7: Reranking bằng RRF (`src/task7_reranking.py`)
- **Thực hiện ra sao:** Lấy danh sách kết quả của Task 5 và Task 6, lặp qua các kết quả này. Gán điểm mới cho từng chunk bằng công thức: $RRF\_Score = \sum \frac{1}{k + rank}$ (với hằng số trơn $k=60$).
- **Tại sao lại làm vậy:** Điểm cosine của Dense Search (vd: 0.8) không cùng thang đo (scale) với điểm của BM25 (vd: 5.6). Không thể cộng trực tiếp hai điểm này với nhau. RRF bỏ qua điểm số thô, chỉ dùng "thứ hạng" (rank) của văn bản để chấm điểm, giúp gộp hai kết quả Hybrid công bằng và tối ưu nhất, đẩy các kết quả xuất hiện ở top của cả 2 thuật toán lên cao nhất.

### Task 8: PageIndex Vectorless Fallback (`src/task8_pageindex_vectorless.py`)
- **Thực hiện ra sao:** Khởi tạo `PageIndexClient`. Xây dựng hàm upload tự động đọc các file, kiểm tra trong file `pageindex_cache.json` xem đã upload chưa. Nếu chưa sẽ đẩy lên PageIndex API và cache lại `doc_id`. Ở hàm search, dùng vòng lặp polling liên tục để lấy status `completed` và trả về kết quả nodes.
- **Tại sao lại làm vậy:** Trong hệ thống RAG, nếu query của User quá lạ lẫm, Dense vector đôi khi không bắt được (score thấp). PageIndex đóng vai trò làm công cụ tìm kiếm bổ trợ dự phòng (fallback). Phải làm cơ chế lưu cache `json` vì nếu cứ gọi API upload lại toàn bộ corpus ở mỗi lượt chạy sẽ tốn kém tiền bạc và gây quá tải timeout không đáng có.

### Task 9: Xây dựng Retrieval Pipeline (`src/task9_retrieval_pipeline.py`)
- **Thực hiện ra sao:** Gộp toàn bộ Task 5, 6, 7, 8 thành một luồng xử lý đồng nhất. Code lấy `best_dense_score` so sánh với ngưỡng `SCORE_THRESHOLD (0.3)`. Nếu thấp hơn, bẫy try-except gọi fallback PageIndex. Nếu PageIndex chết hoặc score đủ cao, dùng RRF Hybrid.
- **Tại sao lại làm vậy:** Kiến trúc này mô phỏng một hệ thống Production thực tế. Luôn ưu tiên dùng bộ search local (Nhanh, Rẻ) bằng Hybrid RRF. Chỉ khi hệ thống không tự tin về câu trả lời (`score < 0.3`) thì mới "tốn tiền" gọi ra API ngoài (Chậm, Đắt). Việc kết hợp Try-Except đảm bảo Pipeline kháng lỗi (Fault Tolerant), user sẽ luôn nhận được một câu trả lời khả dĩ nào đó thay vì màn hình báo lỗi sập server.

## Quyết định kỹ thuật quan trọng

1. **Quyết định:** Chuyển đổi từ `BM25Okapi` sang `BM25Plus` trong quá trình thực hiện Lexical Search (Task 6).
   - **Lý do/evidence:** Trong các bộ test nhỏ (corpus chỉ có 2-3 documents), `BM25Okapi` gặp hiện tượng triệt tiêu điểm số (IDF sinh ra giá trị bằng `0.0` nếu từ khoá có mặt ở đúng 50% số văn bản). Việc đổi qua `BM25Plus` bổ sung thêm một hằng số nhỏ để tránh việc bị 0 điểm, giúp pass mượt mà bộ Unit Test (Contract tests).
   - **Trade-off:** `BM25Plus` có thể làm lệch một chút tỷ lệ phân phối điểm số so với phiên bản BM25 chuẩn ở các bộ dữ liệu siêu lớn, nhưng với hệ thống RAG domain-specific (kích thước vừa phải), sự ổn định được ưu tiên hơn.

2. **Quyết định:** Bẫy lỗi an toàn (Safe Try-Except) trong Pipeline ở Task 9 thay vì ném ra Exception làm crash chatbot.
   - **Lý do/evidence:** Task 8 phụ thuộc vào dịch vụ bên ngoài (PageIndex). Nếu không bẫy lỗi, khi API key hết hạn hoặc server timeout, toàn bộ ứng dụng Streamlit sẽ bị sập. Việc thêm `try-except` cho phép hệ thống fallback trả về kết quả Hybrid nội bộ nếu dịch vụ bên ngoài không phản hồi.
   - **Trade-off:** Che giấu (swallow) lỗi hệ thống nếu không in log đầy đủ. Do đó, cần đảm bảo có cơ chế monitoring trên terminal (báo `Failed to upload`) thay vì để người dùng hoàn toàn không biết.

## Kiểm thử và kết quả

- **Test đã dùng:** Tôi đã sử dụng bộ `pytest tests/test_contracts.py -q` được cấp sẵn trong repo để test liên tục (TDD - Test Driven Development).
- **Kết quả trước/sau:** Ban đầu test bị lỗi (Failed 7/15) do logic BM25 trả về mảng rỗng và lỗi import module, sau khi tinh chỉnh thuật toán BM25 và hoàn thiện hàm query ChromaDB thì đã Pass xanh toàn bộ 15/15 test contract.
- **Lỗi đã phát hiện và cách xử lý:** Phát hiện lỗi `IndexError` khi test `test_lexical_search_returns_bm25_contract` do score trả về `<= 0`. Xử lý bằng cách lọc chặt chẽ các index có điểm `== 0.0` và đổi thuật toán BM25 như đề cập ở phần trên.

## Điều còn hạn chế

- **Một hạn chế cụ thể của phần tôi làm:** Threshold để kích hoạt fallback (`SCORE_THRESHOLD = 0.3`) hiện đang là một con số cứng (hard-coded). Trong thực tế, điểm cosine distance phụ thuộc cực kỳ lớn vào embedding model (ví dụ model `BAAI/bge-m3` có dải điểm phân bố khác so với model `openai/text-embedding-3-small`).
- **Nếu có thêm thời gian, thay đổi đầu tiên tôi sẽ thực hiện:** Viết một đoạn script calibrate (hiệu chuẩn) tự động: chạy thử 50 câu hỏi in-domain và 50 câu out-of-domain để tìm ra ngưỡng threshold tối ưu nhất (cân bằng giữa Precision và Recall) thay vì đoán mò.

## Xác nhận đóng góp

Tôi xác nhận nội dung trên phản ánh đúng phần việc của mình và có thể giải thích hoặc chạy lại trong buổi demo.

- **Ngày:** 25/09/2026
- **Tên thành viên:** Trần Văn Khánh
