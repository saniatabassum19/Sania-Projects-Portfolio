import streamlit as st
from pathlib import Path

from src.loader import DocumentLoader
from src.chunker import TextChunker
from src.embeddings import EmbeddingModel
from src.vectorstore import VectorStoreManager
from src.retriever import RetrieverManager
from src.llm import GeminiRAG

PAGE_ICON = "🤖"

st.set_page_config(page_title="Multimodal RAG Chatbot", page_icon=PAGE_ICON, layout="wide")

st.title("Multimodal RAG Chatbot")
st.markdown(
    "Upload PDFs, images, CSVs, and Excel files, then ask questions based on the uploaded content."
)


def get_file_fingerprint(uploaded_files):
    if not uploaded_files:
        return None
    return tuple((f.name, f.size) for f in uploaded_files)


def load_all_documents(uploaded_files, loader):
    documents = []
    for uploaded_file in uploaded_files:
        uploaded_file.seek(0)
        documents.extend(loader.load_file(uploaded_file))
    return [doc for doc in documents if doc.get("content", "").strip()]


def build_vector_store(uploaded_files):
    loader = DocumentLoader()
    raw_documents = load_all_documents(uploaded_files, loader)
    if not raw_documents:
        raise ValueError("No text could be extracted from the uploaded files.")

    chunks = TextChunker().chunk_documents(raw_documents)
    if not chunks:
        raise ValueError("No chunks were created from the uploaded documents.")

    embedding_model = EmbeddingModel()
    vector_store_manager = VectorStoreManager(embedding_model.get_embeddings_model())
    return vector_store_manager.create_vectorstore(chunks)


def format_sources(sources):
    lines = []
    for source in sources:
        name = source.get("source", "unknown")
        page = source.get("page")
        if page is not None:
            lines.append(f"- {name} (page {page})")
        else:
            lines.append(f"- {name}")
    return "\n".join(lines)


if "vector_store" not in st.session_state:
    st.session_state.vector_store = None
if "file_fingerprint" not in st.session_state:
    st.session_state.file_fingerprint = None
if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Upload documents")
    uploaded_files = st.file_uploader(
        "Select one or more files",
        type=["pdf", "png", "jpg", "jpeg", "csv", "xlsx"],
        accept_multiple_files=True,
    )

    st.markdown("---")
    st.write("Supported file types:")
    st.write("- PDF")
    st.write("- PNG / JPG / JPEG")
    st.write("- CSV")
    st.write("- Excel (.xlsx)")

    if st.button("Clear chat"):
        st.session_state.messages = []

fingerprint = get_file_fingerprint(uploaded_files)

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) uploaded.")
    for uploaded_file in uploaded_files:
        st.write(f"**{uploaded_file.name}** — {uploaded_file.type or 'unknown type'}")

    if fingerprint != st.session_state.file_fingerprint:
        with st.spinner("Processing documents (this may take a minute on first run)..."):
            try:
                st.session_state.vector_store = build_vector_store(uploaded_files)
                st.session_state.file_fingerprint = fingerprint
                st.session_state.messages = []
                st.toast("Documents indexed successfully.", icon="✅")
            except Exception as exc:
                st.session_state.vector_store = None
                st.session_state.file_fingerprint = None
                st.error(f"Failed to process documents: {exc}")
elif st.session_state.vector_store is not None:
    st.session_state.vector_store = None
    st.session_state.file_fingerprint = None
    st.session_state.messages = []
    st.info("Upload files to enable document ingestion and retrieval.")
else:
    st.info("Upload files to enable document ingestion and retrieval.")

st.markdown("---")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message.get("sources"):
            st.markdown("**Sources:**")
            st.markdown(format_sources(message["sources"]))

query = st.chat_input("Ask a question based on the uploaded documents:")

if query:
    if not uploaded_files or st.session_state.vector_store is None:
        st.warning("Please upload and process at least one document before asking a question.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.spinner("Retrieving answer..."):
            try:
                retriever = RetrieverManager(st.session_state.vector_store)
                retrieved_docs = retriever.retrieve(query, k=4)
                result = GeminiRAG().generate_answer(query, retrieved_docs)

                answer = result.get("answer") or "No answer generated."
                sources = result.get("sources") or []

                st.session_state.messages.append(
                    {"role": "assistant", "content": answer, "sources": sources}
                )
            except Exception as exc:
                st.session_state.messages.append(
                    {"role": "assistant", "content": f"Something went wrong: {exc}"}
                )
        st.rerun()

st.sidebar.markdown("---")
index_ready = st.session_state.vector_store is not None
st.sidebar.write("Index status:", "Ready" if index_ready else "Not built")
