from src.loader import DocumentLoader
from src.chunker import TextChunker
from src.embeddings import EmbeddingModel
from src.vectorstore import VectorStoreManager
from src.retriever import RetrieverManager
from src.llm import GeminiRAG


def main():
    pdf_path = "data/pdfs/sample.pdf"
    query = "What is this document about?"

    try:
        loader = DocumentLoader()
        with open(pdf_path, "rb") as pdf_file:
            raw_documents = loader.load_pdf(pdf_file)

        if not raw_documents:
            raise RuntimeError(f"No documents were loaded from {pdf_path}.")

        chunker = TextChunker()
        chunks = chunker.chunk_documents(raw_documents)
        if not chunks:
            raise RuntimeError("Document chunking returned no chunks.")

        embedding_model = EmbeddingModel()
        embeddings = embedding_model.embed_documents(chunks)
        if not embeddings:
            raise RuntimeError("Failed to create embeddings for document chunks.")

        vector_store_manager = VectorStoreManager(embedding_model.get_embeddings_model())
        vector_store = vector_store_manager.create_vectorstore(chunks)
        if vector_store is None:
            raise RuntimeError("FAISS vector store creation failed.")

        retriever_manager = RetrieverManager(vector_store)
        retrieved_docs = retriever_manager.retrieve(query, k=4)
        if not retrieved_docs:
            raise RuntimeError("No documents were retrieved for the query.")

        gemini_rag = GeminiRAG()
        result = gemini_rag.generate_answer(query, retrieved_docs)

        print("Answer\n")
        print(result.get("answer") or "No answer generated.")

        print("\nSources:")
        for source in result.get("sources", []):
            source_name = source.get("source", "unknown")
            page = source.get("page")
            page_info = f"page {page}" if page is not None else "page unknown"
            print(f"{source_name} {page_info}")

    except FileNotFoundError as exc:
        print(f"File not found: {exc}")
    except Exception as exc:
        print(f"Pipeline failed: {exc}")


if __name__ == "__main__":
    main()
