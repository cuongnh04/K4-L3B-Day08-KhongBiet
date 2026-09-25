import sys
from pathlib import Path
from fpdf import FPDF


class CustomPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("ArialVN", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(
                0,
                6,
                "Lab Day 8: RAG Pipeline | Báo cáo Dữ liệu & Hướng dẫn Demo (Task 1-3) - Nhóm K4-L3B-Day08-KhongBiet",
                border="B",
                align="L",
            )
            self.ln(6)

    def footer(self):
        self.set_y(-12)
        self.set_font("ArialVN", "I", 8)
        self.set_text_color(120, 120, 120)
        self.cell(
            0,
            6,
            f"Trang {self.page_no()}/{{nb}}  |  Người thực hiện: Đậu Quang Ý (MSSV: 2A202602661)",
            border="T",
            align="R",
        )

    def section_title(self, title: str):
        self.set_font("ArialVN", "B", 13)
        self.set_text_color(16, 52, 96)  # Deep Navy Blue
        self.set_fill_color(235, 243, 250)
        self.cell(0, 8, f"  {title}", ln=True, fill=True)
        self.ln(3)

    def sub_title(self, title: str):
        self.set_font("ArialVN", "B", 10.5)
        self.set_text_color(28, 90, 130)
        self.cell(0, 6, title, ln=True)
        self.ln(1)

    def body_p(self, text: str):
        self.set_font("ArialVN", "", 9.5)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5, text)
        self.ln(2)

    def bullet_point(self, bold_prefix: str, content: str):
        self.set_font("ArialVN", "B", 9.5)
        self.set_text_color(30, 30, 30)
        prefix = f"  * {bold_prefix}: " if bold_prefix else "  * "
        width = self.get_string_width(prefix)
        self.write(5, prefix)
        self.set_font("ArialVN", "", 9.5)
        self.write(5, content)
        self.ln(5.5)

    def callout_box(self, title: str, text: str, bg_color=(245, 248, 255), border_color=(70, 130, 180)):
        self.set_fill_color(*bg_color)
        self.set_draw_color(*border_color)
        self.set_line_width(0.4)
        
        # Save current position
        start_x = self.get_x()
        start_y = self.get_y()
        width = self.epw

        self.set_font("ArialVN", "B", 9.5)
        self.set_text_color(16, 52, 96)
        
        # Calculate height roughly
        self.ln(2)
        self.cell(4) # indent
        self.cell(0, 5, title, ln=True)
        self.set_font("ArialVN", "", 9)
        self.set_text_color(40, 40, 40)
        self.cell(4)
        self.multi_cell(width - 8, 4.5, text)
        self.ln(2)
        end_y = self.get_y()
        
        # Draw rect
        box_h = end_y - start_y
        self.rect(start_x, start_y, width, box_h, style="DF")
        
        # Re-write text over rect
        self.set_y(start_y + 2)
        self.set_x(start_x + 4)
        self.set_font("ArialVN", "B", 9.5)
        self.set_text_color(16, 52, 96)
        self.cell(0, 5, title, ln=True)
        self.set_x(start_x + 4)
        self.set_font("ArialVN", "", 9)
        self.set_text_color(40, 40, 40)
        self.multi_cell(width - 8, 4.5, text)
        self.set_y(end_y + 3)


def build_pdf(output_path: Path):
    pdf = CustomPDF(orientation="P", unit="mm", format="A4")
    pdf.set_margins(15, 15, 15)
    pdf.set_auto_page_break(auto=True, margin=15)

    # Add Vietnamese Fonts
    pdf.add_font("ArialVN", "", r"C:\Windows\Fonts\arial.ttf")
    pdf.add_font("ArialVN", "B", r"C:\Windows\Fonts\arialbd.ttf")
    pdf.add_font("ArialVN", "I", r"C:\Windows\Fonts\ariali.ttf")

    pdf.add_page()

    # COVER / HEADER BLOCK
    pdf.set_font("ArialVN", "B", 16)
    pdf.set_text_color(16, 52, 96)
    pdf.cell(0, 8, "LAB DAY 8 — RAG PIPELINE (BÀI TẬP NHÓM)", align="C", ln=True)
    
    pdf.set_font("ArialVN", "B", 13)
    pdf.set_text_color(220, 53, 69) # Red highlight
    pdf.cell(0, 7, "TÀI LIỆU KỸ THUẬT: DỮ LIỆU, LÀM SẠCH VÀ HƯỚNG DẪN DEMO", align="C", ln=True)
    
    pdf.set_font("ArialVN", "I", 9.5)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 5, "Dành riêng cho Nhóm trưởng & Thành viên nhóm chuẩn bị Demo nghiệm thu", align="C", ln=True)
    pdf.ln(3)

    # Info table box
    pdf.set_fill_color(248, 249, 250)
    pdf.set_draw_color(200, 200, 200)
    pdf.rect(15, pdf.get_y(), pdf.epw, 20, style="DF")
    pdf.set_y(pdf.get_y() + 2)
    
    col_w = pdf.epw / 2
    pdf.set_font("ArialVN", "B", 9)
    pdf.set_text_color(40, 40, 40)
    pdf.cell(col_w, 5, "  * Người phụ trách: Đậu Quang Ý (MSSV: 2A202602661)", ln=False)
    pdf.cell(col_w, 5, "* Nhóm: K4-L3B-Day08-KhongBiet", ln=True)
    pdf.cell(col_w, 5, "  * Nhiệm vụ: Task 1, Task 2, Task 3 (Data Pipeline)", ln=False)
    pdf.cell(col_w, 5, "* Repo Git: cuongnh04/K4-L3B-Day08-KhongBiet", ln=True)
    pdf.cell(col_w, 5, "  * Trạng thái nghiệm thu: PASS 3/3 Acceptance Tests (100%)", ln=False)
    pdf.cell(col_w, 5, "* Ngày hoàn thành: 25/09/2026", ln=True)
    pdf.ln(5)

    # SECTION 1
    pdf.section_title("I. TỔNG QUAN ĐỀ TÀI & DANH MỤC TÀI LIỆU THU THẬP")
    pdf.body_p(
        "Nhóm đã lựa chọn đề tài: 'Quy chế đào tạo, học bổng & dịch vụ sinh viên Đại học' "
        "(sử dụng nguồn dữ liệu chính quy từ Trường ĐH Công nghệ Thông tin - ĐHQG-HCM). "
        "Đây là bài toán thực tiễn cao, đáp ứng đầy đủ điều kiện cho chatbot RAG giải đáp mọi thắc mắc của sinh viên."
    )

    pdf.sub_title("1. Khối tài liệu Pháp lý / Quy chế (Legal Docs - Task 1)")
    pdf.body_p("Lưu tại thư mục data/landing/legal/ (được lọc chọn PDF số hóa gốc có Text Layer, dung lượng > 280KB/file):")
    
    pdf.bullet_point("quy_che_dao_tao_dai_hoc.pdf (533.8 KB)", "27 trang quy định toàn diện về đào tạo tín chỉ, đăng ký học phần, thời gian học tập tối đa, kiểm tra đánh giá, cảnh báo học vụ, thôi học và điều kiện xét công nhận tốt nghiệp.")
    pdf.bullet_point("quy_dinh_danh_gia_ren_luyen.pdf (594.1 KB)", "17 trang quy chế khung điểm rèn luyện, 5 tiêu chí chấm điểm (học tập, kỷ luật, phong trào đoàn thể, quan hệ cộng đồng, hoạt động đặc biệt) và phân loại Xuất sắc/Tốt/Khá.")
    pdf.bullet_point("quy_che_an_toan_thong_tin.pdf (281.4 KB)", "16 trang quy định về bảo đảm an toàn thông tin, quyền và trách nhiệm của sinh viên khi sử dụng tài khoản email trường, mạng nội bộ và hệ thống học trực tuyến.")
    pdf.bullet_point("quy_che_dao_tao_ngoai_ngu.pdf (402.2 KB)", "Văn bản quy định về chuẩn đầu ra ngoại ngữ (tiếng Anh/IELTS/TOEIC), quy trình xét miễn học phần và lộ trình hoàn thành chứng chỉ.")

    pdf.sub_title("2. Khối bài viết Thông báo / Tin tức (News Articles - Task 2)")
    pdf.body_p("Lưu tại thư mục data/landing/news/*.json (gồm 5 bài viết trích xuất đầy đủ URL, Tiêu đề, Thời gian và Markdown):")
    
    pdf.bullet_point("article_01.json", "Hướng dẫn quy định mới về xét cấp học bổng khuyến khích học tập (áp dụng từ HK1 năm học 2026-2027).")
    pdf.bullet_point("article_02.json", "Các điều kiện tiên quyết để nhận học bổng: không nợ học phí, không vi phạm kỷ luật và phải có bảo hiểm y tế.")
    pdf.bullet_point("article_03.json", "Danh sách dự kiến và hướng dẫn cập nhật số tài khoản ngân hàng chính chủ để nhận học bổng.")
    pdf.bullet_point("article_04.json", "Thông báo học bổng ngoại ngữ UIT Global và các quyền lợi phát triển kỹ năng quốc tế.")
    pdf.bullet_point("article_05.json", "Chính sách học phí, miễn giảm học phí và các chế độ trợ cấp xã hội dành cho sinh viên chính sách, khó khăn.")

    pdf.ln(2)

    # SECTION 2
    pdf.section_title("II. CẤU TRÚC TỔ CHỨC DỮ LIỆU TRONG REPOSITORY")
    pdf.body_p("Kiến trúc thư mục tuân thủ nghiêm ngặt chuẩn thiết kế RAG Pipeline của bài lab:")
    
    pdf.callout_box(
        "KIẾN TRÚC THƯ MỤC DỮ LIỆU (DATA ARCHITECTURE)",
        "data/\n"
        "├── landing/                # Dữ liệu thu thập ban đầu (Thô)\n"
        "│   ├── legal/              # Chứa 4 file PDF quy chế chính thức (> 280KB/file)\n"
        "│   └── news/               # Chứa 5 file JSON bài viết tin tức\n"
        "└── standardized/           # Dữ liệu đã làm sạch & chuẩn hóa sang Markdown\n"
        "    ├── legal/              # 4 file .md (dài từ 28.600 đến 65.200 ký tự)\n"
        "    └── news/               # 5 file .md (dài từ 1.900 đến 9.000 ký tự, có Header Metadata)\n\n"
        "-> Cấu trúc JSON Landing: {\"url\": ..., \"title\": ..., \"date_crawled\": ..., \"content_markdown\": ...}\n"
        "-> Cấu trúc Markdown News: Header chuẩn (# Title, Source, Date) + Đường kẻ ngang '---' + Nội dung."
    )

    pdf.add_page()

    # SECTION 3
    pdf.section_title("III. TẠI SAO PHẢI LÀM SẠCH DỮ LIỆU? (THE 'WHY')")
    pdf.body_p(
        "Trong kỹ thuật RAG, chất lượng câu trả lời của mô hình phụ thuộc hoàn toàn vào ngữ cảnh "
        "được truy xuất (Context Retrieval). Làm sạch dữ liệu là bước then chốt quyết định vì các lý do sống còn sau:"
    )

    pdf.bullet_point(
        "1. Triệt tiêu 'nhiễu' cho Hybrid Search",
        "Trang web thô chứa rất nhiều menu (<nav>), banner, footer, mã JavaScript/CSS. "
        "Nếu không làm sạch, thuật toán BM25 sẽ bị phân tán bởi các từ khóa xuất hiện lặp lại "
        "(như 'Trang chủ', 'Liên hệ'), còn Dense Vector Search sẽ sinh ra vector ngữ nghĩa bị sai hướng."
    )
    pdf.bullet_point(
        "2. Bảo toàn cấu trúc ngữ nghĩa cho Chunking (Task 4)",
        "Văn bản quy chế đào tạo phân cấp theo: Chương -> Điều -> Khoản -> Điểm. "
        "Việc chuẩn hóa sang Markdown (sử dụng #, ##, danh sách, bảng biểu |---|) "
        "giúp Text Splitter cắt theo đúng phạm vi điều khoản, không bị đứt gãy giữa điều kiện và kết quả."
    )
    pdf.bullet_point(
        "3. Tiết kiệm Token và mở rộng Cửa sổ ngữ cảnh (Context Window)",
        "Mã nguồn HTML rác chiếm tới 70-80% dung lượng. Loại bỏ HTML rác giúp giảm chi phí gọi API (OpenAI/Gemini), "
        "đồng thời cho phép nhồi được nhiều đoạn trích hữu ích (top-k chunks) vào prompt của LLM."
    )
    pdf.bullet_point(
        "4. Cung cấp Metadata bắt buộc phục vụ Trích dẫn (Citation ở Task 10)",
        "Chatbot RAG bắt buộc phải trích dẫn nguồn kiểm chứng để chống ảo giác (hallucination). "
        "Việc làm sạch và đưa URL, Tiêu đề, Ngày crawl vào Header giúp LLM dễ dàng trích dẫn nguồn chính xác."
    )
    pdf.bullet_point(
        "5. Ngăn ngừa tài liệu scan rỗng và lỗi vỡ font tiếng Việt",
        "Nếu dùng file scan ảnh chụp mờ, công cụ đọc text sẽ trả về rỗng (0 ký tự). "
        "Bên cạnh đó, việc ép chuẩn UTF-8 loại bỏ hoàn toàn lỗi mã hóa font tiếng Việt (charmap/cp1252) trên Windows."
    )

    pdf.ln(2)

    # SECTION 4
    pdf.section_title("IV. ĐÃ LÀM SẠCH DỮ LIỆU NHƯ THẾ NÀO? (THE 'HOW')")
    pdf.body_p("Quy trình làm sạch được tự động hóa qua 2 pipeline độc lập và chặt chẽ:")

    pdf.sub_title("1. Pipeline Bài viết Web (HTML -> JSON -> Markdown) tại src/task2 & task3")
    pdf.bullet_point("Container Filtering", "Dùng BeautifulSoup tìm chính xác khối nội dung bài viết (div.field-name-body, article), triệt tiêu hoàn toàn header, menu, sidebar và chân trang.")
    pdf.bullet_point("Tag Stripping", "Dùng thư viện markdownify với bộ lọc strip=['script', 'style', 'nav', 'footer'] để dọn dẹp sạch mã kỹ thuật rác.")
    pdf.bullet_point("Header Normalization", "Tự động đóng gói tiêu đề (# Title), URL nguồn (**Source:**) và thời gian crawl (**Crawled:**) vào đầu mỗi file markdown chuẩn hóa.")

    pdf.sub_title("2. Pipeline Quy chế Pháp lý (PDF -> Markdown) tại src/task1 & task3")
    pdf.bullet_point("Sàng lọc Digital Text Layer", "Lọc bỏ các file scan ảnh mờ, chỉ chọn 4 văn bản quy chế PDF số hóa chính thức của trường có lớp chữ vector sắc nét.")
    pdf.bullet_point("MarkItDown Engine Chuyên sâu", "Cấu hình MarkItDown tích hợp pdfminer-six và pdfplumber, tự động chuyển đổi cấu trúc chương điều và bảng biểu quy chế thành bảng Markdown chuẩn | Cột 1 | Cột 2 |.")
    pdf.bullet_point("Mã hóa UTF-8", "Toàn bộ dữ liệu được ghi với encoding='utf-8', bảo đảm hiển thị tiếng Việt hoàn hảo trên mọi nền tảng.")

    pdf.add_page()

    # SECTION 5
    pdf.section_title("V. HƯỚNG DẪN DÀNH CHO NHÓM TRƯỞNG KHI BÁO CÁO & DEMO")
    pdf.body_p(
        "Tài liệu này cung cấp các kịch bản thực chiến giúp Nhóm trưởng và các thành viên tự tin demo "
        "và trả lời câu hỏi vấn đáp của Giảng viên về phần dữ liệu (Task 1 - 3):"
    )

    pdf.callout_box(
        "LỆNH CHẠY KIỂM THỬ ACCEPTANCE TESTS CHO THẦY CÔ XEM",
        "Nhóm trưởng mở terminal và chạy lệnh:\n"
        "    pytest tests/test_acceptance.py -k \"test_corpus or test_standardized\" -v\n\n"
        "Kết quả hiển thị trên màn hình:\n"
        "    test_corpus_has_required_legal_documents        PASSED [ 33%]\n"
        "    test_corpus_has_required_news_with_metadata     PASSED [ 66%]\n"
        "    test_standardized_output_covers_both_source_types PASSED [100%]\n"
        "-> Minh chứng 100% tiêu chí chấp thuận của bài lab đã đạt tuyệt đối!"
    )

    pdf.ln(1)
    pdf.sub_title("Bộ 4 câu hỏi mẫu (Sample Queries) chuẩn bị sẵn cho Chatbot Demo:")
    pdf.bullet_point("Câu hỏi 1 (Về Học bổng)", "'Điều kiện để sinh viên được xét cấp học bổng khuyến khích học tập là gì?' -> Chatbot sẽ trích xuất từ article_01, article_02: không nợ học phí, có BHYT, điểm rèn luyện Khá trở lên.")
    pdf.bullet_point("Câu hỏi 2 (Về Quy chế đào tạo)", "'Khi nào sinh viên bị cảnh báo học vụ theo quy chế của trường?' -> Chatbot sẽ trích xuất từ quy_che_dao_tao_dai_hoc.md: điểm trung bình học kỳ dưới ngưỡng, nợ tín chỉ tích lũy quá hạn.")
    pdf.bullet_point("Câu hỏi 3 (Về Ngoại ngữ)", "'Quy định chuẩn đầu ra ngoại ngữ và trường hợp nào được xét miễn học phần tiếng Anh?' -> Chatbot trích xuất từ quy_che_dao_tao_ngoai_ngu.md: chứng chỉ IELTS, TOEIC quốc tế tương đương.")
    pdf.bullet_point("Câu hỏi 4 (Về Điểm rèn luyện)", "'Khung điểm rèn luyện gồm những tiêu chí nào và bao nhiêu điểm thì đạt loại Xuất sắc?' -> Chatbot trích xuất từ quy_dinh_danh_gia_ren_luyen.md: 5 tiêu chí đánh giá, từ 90 đến 100 điểm.")

    pdf.ln(1)
    pdf.sub_title("Bí quyết trả lời câu hỏi vấn đáp của Giảng viên:")
    pdf.bullet_point(
        "Nếu thầy cô hỏi: 'Dữ liệu nhóm lấy từ đâu, có sạch không?'",
        "Trả lời: Dữ liệu được nhóm thu thập chính thống từ Trường ĐH Công nghệ Thông tin - ĐHQG-HCM. Nhóm đã xây dựng pipeline làm sạch tự động bằng BeautifulSoup và MarkItDown, loại bỏ hoàn toàn boilerplate HTML và chuyển đổi cấu trúc phân cấp sang Markdown có gắn Metadata trích dẫn."
    )
    pdf.bullet_point(
        "Nếu thầy cô hỏi: 'Làm sao đảm bảo chatbot không bị ảo giác (hallucination)?'",
        "Trả lời: Nhóm đã chèn Source URL và Date Crawled ngay từ khâu tiền xử lý (Task 3). Điều này giúp Retrieval Pipeline lọc chính xác và prompt ở Task 10 buộc LLM chỉ trả lời dựa trên context được cung cấp kèm citation rõ ràng."
    )

    # Footer note
    pdf.ln(4)
    pdf.set_font("ArialVN", "I", 9)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 5, "* Toàn bộ mã nguồn, dữ liệu và báo cáo đã được đồng bộ lên Git commit a0179e5 & 08ef561 trên branch main.", align="C", ln=True)

    pdf.output(str(output_path))
    print(f"Generated PDF successfully at: {output_path}")


if __name__ == "__main__":
    out = Path(__file__).parent.parent / "reports" / "BAO_CAO_DU_LIEU_VA_DEMO_TASK1_3.pdf"
    build_pdf(out)
