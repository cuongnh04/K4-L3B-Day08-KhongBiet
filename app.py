import html
import os
import re
import streamlit as st
from dotenv import load_dotenv

from src.task10_generation import generate_with_citation, generate_ab_comparison

load_dotenv()

# Cấu hình trang
st.set_page_config(
    page_title="Trợ lý RAG — Quy chế & Dịch vụ Sinh viên",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS tái hiện chính xác thiết kế Mockup trong ảnh
st.markdown(
    """
    <style>
    /* Nền tổng thể màu be ấm cao cấp */
    .stApp {
        background-color: #FAF7F2;
        color: #2D2926;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 5rem;
        max-width: 960px;
    }

    /* Thanh điều hướng Header */
    .header-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 1rem;
        border-bottom: 1px solid #EAE3D9;
        margin-bottom: 1.5rem;
    }
    .header-title {
        font-family: "Newsreader", "Playfair Display", Georgia, serif;
        font-size: 1.6rem;
        font-weight: 600;
        color: #1A1816;
    }

    /* Hero Empty State */
    .hero-container {
        text-align: center;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    .hero-title {
        font-family: "Newsreader", "Playfair Display", Georgia, serif;
        font-size: 2.6rem;
        font-weight: 700;
        color: #1A1816;
        margin-bottom: 0.6rem;
    }
    .hero-title span {
        color: #BA522B;
    }
    .hero-subtitle {
        color: #7A7269;
        font-size: 1.05rem;
        max-width: 580px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* Tin nhắn người dùng */
    .user-bubble-container {
        display: flex;
        justify-content: flex-end;
        margin: 1.2rem 0;
    }
    .user-bubble {
        background-color: #BA522B;
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 20px;
        max-width: 85%;
        font-size: 1rem;
        line-height: 1.5;
        box-shadow: 0 2px 6px rgba(186, 82, 43, 0.15);
    }

    /* Tin nhắn bot & Avatar */
    .bot-container {
        display: flex;
        gap: 12px;
        margin: 1.2rem 0 0.5rem 0;
    }
    .bot-avatar {
        width: 32px;
        height: 32px;
        border-radius: 6px;
        background-color: #556B2F;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 14px;
        font-weight: bold;
        flex-shrink: 0;
    }
    .bot-name {
        font-size: 0.85rem;
        color: #7A7269;
        font-weight: 500;
        margin-bottom: 6px;
    }
    .bot-text {
        font-size: 1.02rem;
        line-height: 1.65;
        color: #2D2926;
    }

    /* Badge trích dẫn số inline: [1], [2] */
    .cite-pill {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background-color: #F1E3D9;
        color: #9C4220;
        border-radius: 6px;
        padding: 1px 7px;
        font-size: 0.78rem;
        font-weight: 700;
        margin: 0 3px;
        vertical-align: middle;
    }

    /* Khối Nguồn tham khảo */
    .sources-container {
        background-color: white;
        border: 1px solid #EBE4D9;
        border-radius: 14px;
        padding: 18px 22px;
        margin-top: 1.2rem;
        margin-bottom: 1.8rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }
    .sources-header {
        font-size: 0.76rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        color: #9E968D;
        text-transform: uppercase;
        padding-bottom: 8px;
        border-bottom: 1px solid #F0EAE1;
        margin-bottom: 14px;
    }
    .source-item {
        margin-bottom: 16px;
    }
    .source-item:last-child {
        margin-bottom: 0;
    }
    .source-head {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 4px;
    }
    .source-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 20px;
        height: 20px;
        background-color: #F1E3D9;
        color: #9C4220;
        border-radius: 5px;
        font-size: 0.75rem;
        font-weight: 700;
        flex-shrink: 0;
    }
    .source-title {
        font-weight: 600;
        font-size: 0.95rem;
        color: #2D2926;
    }
    .source-sub {
        font-size: 0.82rem;
        color: #8C847B;
        margin-left: 28px;
        margin-bottom: 6px;
    }
    .source-quote {
        background-color: #F5EFE8;
        border-left: 3px solid #BA522B;
        border-radius: 0 8px 8px 0;
        padding: 9px 13px;
        font-size: 0.88rem;
        color: #4A443E;
        line-height: 1.5;
        margin-left: 28px;
    }

    /* Thẻ cột So sánh A/B */
    .ab-card {
        background: white;
        border: 1px solid #EBE4D9;
        border-radius: 12px;
        padding: 16px;
        margin-top: 10px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.03);
    }
    .ab-badge {
        display: inline-block;
        font-size: 0.8rem;
        font-weight: 700;
        padding: 4px 12px;
        border-radius: 6px;
        margin-bottom: 12px;
    }
    .ab-badge-dense {
        background-color: #E2E8F0;
        color: #334155;
    }
    .ab-badge-hybrid {
        background-color: #FEF3C7;
        color: #92400E;
    }

    .disclaimer-text {
        text-align: center;
        font-size: 0.78rem;
        color: #9E968D;
        margin-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Khởi tạo session state
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar cấu hình
with st.sidebar:
    st.title("⚙️ Cấu hình hệ thống")
    st.caption("Day 8 — RAG Pipeline Assistant")

    mode = st.radio(
        "🎯 Chọn chế độ hoạt động:",
        ["🌟 Hybrid (Dense + BM25)", "🧠 Semantic (Dense-only)", "⚖️ So sánh A/B (Side-by-side)"],
        index=0,
    )

    top_k = st.slider("Số lượng chunks retrieval (top_k)", 2, 8, 5)

    provider = os.getenv("LLM_PROVIDER", "gemini").upper()
    model = os.getenv("LLM_MODEL", "Mặc định")
    st.markdown(f"**Provider LLM:** `{provider}`")
    st.markdown(f"**Model:** `{model}`")

    st.markdown("---")
    st.markdown("🛡️ **Bảo mật:** `Prompt Injection Guard: BẬT`")
    st.markdown("📊 **Đánh giá:** `A/B Config A (Dense) vs Config B (Hybrid)`")

    if st.button("🗑️ Xóa lịch sử trò chuyện", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# Thanh tiêu đề phía trên
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown('<div class="header-title">Chính sách đào tạo & Dịch vụ sinh viên</div>', unsafe_allow_html=True)
with col_h2:
    if st.button("Màn hình trống", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# Hàm render citation badges
def render_inline_citations(text: str) -> str:
    return re.sub(r"\[(?:Document\s*)?(\d+)\]", r'<span class="cite-pill">\1</span>', text)


def render_sources_box(sources: list[dict]):
    if not sources:
        return ""
    items = []
    for idx, src in enumerate(sources, 1):
        meta = src.get("metadata", {})
        title = meta.get("title") or meta.get("source", f"Tài liệu {idx}")
        score = src.get("score", 0.0)
        method = src.get("retrieval_method", "hybrid")
        content = src.get("content", "").strip()
        snippet = content[:240] + "..." if len(content) > 240 else content
        items.append(
            f"""
            <div class="source-item">
                <div class="source-head">
                    <span class="source-badge">{idx}</span>
                    <span class="source-title">{html.escape(title)}</span>
                </div>
                <div class="source-sub">Độ khớp: {score:.2f} · Phương thức: {method}</div>
                <div class="source-quote">"{html.escape(snippet)}"</div>
            </div>
            """
        )
    return f"""
    <div class="sources-container">
        <div class="sources-header">Nguồn tham khảo & Đoạn trích</div>
        {''.join(items)}
    </div>
    """


# Chế độ A/B So sánh song song
if mode == "⚖️ So sánh A/B (Side-by-side)":
    st.info("⚖️ **Chế độ So sánh A/B**: Mỗi câu hỏi sẽ được gửi đồng thời qua 2 pipeline: **Config A (Semantic / Dense-only)** và **Config B (Hybrid + RRF)** để đối chiếu câu trả lời và độ chính xác.")

    query = st.chat_input("Nhập câu hỏi để so sánh Semantic vs Hybrid...")

    # Nút câu hỏi gợi ý nhanh
    col_q1, col_q2 = st.columns(2)
    with col_q1:
        if st.button("📌 So sánh: Điều kiện xét học bổng loại Giỏi"):
            query = "Điều kiện xét học bổng khuyến khích loại Giỏi là gì?"
    with col_q2:
        if st.button("📌 So sánh: Quy định cảnh báo học tập mức 1"):
            query = "Sinh viên bị cảnh báo học tập mức 1 khi nào?"

    if query:
        with st.spinner("Đang chạy đồng thời Semantic và Hybrid retrieval..."):
            ab_data = generate_ab_comparison(query, top_k=top_k)

        st.markdown(f"### ❓ Câu hỏi: *{query}*")

        col_a, col_b = st.columns(2)
        with col_a:
            st.markdown('<div class="ab-card"><span class="ab-badge ab-badge-dense">Config A: Semantic Search (Dense-only)</span>', unsafe_allow_html=True)
            res_a = ab_data["semantic_dense"]
            st.markdown(render_inline_citations(res_a["answer"]), unsafe_allow_html=True)
            st.markdown(render_sources_box(res_a["sources"]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col_b:
            st.markdown('<div class="ab-card"><span class="ab-badge ab-badge-hybrid">Config B: Hybrid (Dense + BM25 + RRF)</span>', unsafe_allow_html=True)
            res_b = ab_data["hybrid_rrf"]
            st.markdown(render_inline_citations(res_b["answer"]), unsafe_allow_html=True)
            st.markdown(render_sources_box(res_b["sources"]), unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

else:
    # Chế độ trò chuyện tiêu chuẩn
    os.environ["RETRIEVAL_STRATEGY"] = "dense" if "Dense" in mode else "hybrid"

    # Hiển thị Hero khi chưa có tin nhắn
    if not st.session_state.messages:
        st.markdown(
            """
            <div class="hero-container">
                <div class="hero-title">Hỏi bất cứ điều gì từ <span>tài liệu</span> của bạn</div>
                <div class="hero-subtitle">Trợ lý sẽ tìm trong kho tài liệu đã nạp và trả lời kèm trích dẫn nguồn cụ thể.</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        prompts = [
            ("Tóm tắt điều kiện học bổng", "Tiêu chuẩn GPA và điểm rèn luyện để được xét học bổng khuyến khích"),
            ("Quy định xử lý cảnh báo học tập", "Các mức cảnh báo học tập và điều kiện bị buộc thôi học"),
            ("Quy trình đăng ký nội trú Ký túc xá", "Đối tượng ưu tiên và thủ tục hồ sơ đăng ký KTX sinh viên"),
            ("Điều kiện bảo lưu kết quả học tập", "Thủ tục và thời hạn tối đa được bảo lưu điểm thi"),
        ]

        selected_prompt = None
        for p_title, p_desc in prompts:
            if st.button(f"**{p_title}**\n\n{p_desc}", key=p_title, use_container_width=True):
                selected_prompt = p_title

        if selected_prompt:
            st.session_state.messages.append({"role": "user", "content": selected_prompt})
            st.rerun()

    # Hiển thị lịch sử hội thoại
    for msg in st.session_state.messages:
        if msg["role"] == "user":
            st.markdown(
                f"""
                <div class="user-bubble-container">
                    <div class="user-bubble">{html.escape(msg['content'])}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            formatted_answer = render_inline_citations(msg["content"])
            st.markdown(
                f"""
                <div class="bot-container">
                    <div class="bot-avatar">🤖</div>
                    <div style="flex: 1;">
                        <div class="bot-name">Trợ lý RAG</div>
                        <div class="bot-text">{formatted_answer}</div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(render_sources_box(msg.get("sources", [])), unsafe_allow_html=True)

    query = st.chat_input("Hỏi tiếp về tài liệu này...")

    if query:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.spinner("Đang tra cứu tài liệu và đối chiếu quy chế..."):
            result = generate_with_citation(query, top_k=top_k)
            answer = result.get("answer", "Không thể sinh câu trả lời.")
            sources = result.get("sources", [])

        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": answer,
                "sources": sources,
            }
        )
        st.rerun()

st.markdown(
    '<div class="disclaimer-text">Trợ lý có thể nhầm lẫn — luôn kiểm tra lại nguồn trích dẫn.</div>',
    unsafe_allow_html=True,
)
