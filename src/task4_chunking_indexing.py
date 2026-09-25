"""
Task 4 — Chunking, embedding và indexing.

Hướng dẫn:
    1. Đọc toàn bộ Markdown trong data/standardized/.
    2. Chia văn bản bằng strategy đã chọn.
    3. Embed chunks bằng một provider duy nhất.
    4. Upsert vào ChromaDB với cosine distance.

Mỗi document/chunk phải theo docs/MODULE_CONTRACTS.md. ID cần ổn định để
chạy lại pipeline không tạo dữ liệu trùng. Task 5 phải dùng chung embed_texts().
"""

from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


STANDARDIZED_DIR = Path(__file__).parent.parent / "data" / "standardized"
CHROMA_DIR = Path(__file__).parent.parent / "chroma_db"

# Giải thích lựa chọn tham số trong báo cáo nhóm.
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
CHUNKING_METHOD = "recursive"

EMBEDDING_MODEL = "gemini-embedding-2" # Model theo yêu cầu của user, hoặc có thể dùng "text-embedding-004"
EMBEDDING_DIM = 768 # Gemini embeddings thường có 768 chiều

COLLECTION_NAME = "rag_documents"


def embed_texts(texts: list[str]) -> list[list[float]]:
    import os
    from google import genai
    
    # Khởi tạo client, lấy GEMINI_API_KEY từ biến môi trường
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", ""))
    
    # Gọi API Google GenAI để lấy vector
    result = client.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=texts
    )
    
    # Trích xuất danh sách các vector (nếu truyền 1 text thì là result.embeddings[0].values)
    # Nếu truyền mảng texts, result.embeddings sẽ là mảng chứa các object có thuộc tính values.
    # Tuy nhiên, tuỳ phiên bản SDK, có thể trả về mảng trực tiếp hoặc mảng objects.
    # Trong google-genai mới nhất:
    try:
        return [emb.values for emb in result.embeddings]
    except AttributeError:
        # Trong trường hợp SDK trả về kiểu khác (như dictionary)
        return [emb["values"] if isinstance(emb, dict) else emb for emb in result.embeddings]


def get_collection():
    """Mở Chroma collection dùng cosine distance."""
    import chromadb
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def load_documents() -> list[dict]:
    """Đọc Markdown và trả về danh sách Document."""
    documents = []
    for path in STANDARDIZED_DIR.rglob("*.md"):
        doc_type = "legal" if "legal" in path.parts else "news"
        documents.append({
            "id": path.relative_to(STANDARDIZED_DIR).as_posix(),
            "content": path.read_text(encoding="utf-8"),
            "metadata": {
                "source": path.name,
                "title": path.stem,
                "doc_type": doc_type,
                "url": None,
            },
        })
    return documents


def chunk_documents(documents: list[dict]) -> list[dict]:
    """Chia Document thành chunks có id và chunk_index."""
    from langchain_text_splitters import RecursiveCharacterTextSplitter, MarkdownHeaderTextSplitter
    
    headers_to_split_on = [
        ("#", "Header 1"),
        ("##", "Header 2"),
        ("###", "Header 3"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on)
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = []
    for document in documents:
        # Tách theo header markdown (Chương, Điều, Khoản...)
        try:
            md_docs = md_splitter.split_text(document["content"])
        except Exception:
            # Fallback nếu lỗi
            from langchain_core.documents import Document
            md_docs = [Document(page_content=document["content"], metadata={})]
            
        chunk_idx = 0
        for md_doc in md_docs:
            # Nhúng thông tin header vào text để không bị mất context khi nhúng (embed)
            header_context = " ".join([f"{k}: {v}" for k, v in md_doc.metadata.items()])
            full_text = f"{header_context}\n\n{md_doc.page_content}" if header_context else md_doc.page_content
            
            # Tiếp tục tách nhỏ nếu quá dài
            for text in splitter.split_text(full_text):
                chunks.append({
                    "id": f"{document['id']}::chunk-{chunk_idx}",
                    "content": text,
                    "metadata": {**document["metadata"], "chunk_index": chunk_idx},
                })
                chunk_idx += 1
    return chunks


def embed_chunks(chunks: list[dict]) -> list[dict]:
    """Thêm embedding vào từng chunk."""
    vectors = embed_texts([chunk["content"] for chunk in chunks])
    for chunk, vector in zip(chunks, vectors):
        chunk["embedding"] = vector
    return chunks


def index_to_vectorstore(chunks: list[dict]) -> None:
    """Upsert chunks vào ChromaDB."""
    collection = get_collection()
    collection.upsert(
        ids=[chunk["id"] for chunk in chunks],
        documents=[chunk["content"] for chunk in chunks],
        embeddings=[chunk["embedding"] for chunk in chunks],
        metadatas=[chunk["metadata"] for chunk in chunks],
    )


def run_pipeline() -> None:
    """Chạy load, chunk, embed và index."""
    documents = load_documents()
    chunks = chunk_documents(documents)
    embedded_chunks = embed_chunks(chunks)
    index_to_vectorstore(embedded_chunks)
    print(f"Indexed {len(embedded_chunks)} chunks")


if __name__ == "__main__":
    run_pipeline()
