"""Vector store utilities for multimodal RAG."""

from typing import List, Optional

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document


class VectorStoreManager:
    """Manage FAISS vector store operations."""

    def __init__(self, embedding_model):
        self.embedding_model = embedding_model
        self.vector_store: Optional[FAISS] = None

    def create_vectorstore(self, documents: List[Document]) -> FAISS:
        """Create a FAISS vector store from documents and embeddings."""
        if not isinstance(documents, list):
            raise ValueError("documents must be a list of LangChain Document objects.")

        try:
            self.vector_store = FAISS.from_documents(
                documents, self.embedding_model
            )
            return self.vector_store
        except Exception as exc:
            raise RuntimeError(f"Failed to create FAISS vector store: {exc}") from exc

    def save_vectorstore(self, path: str = "faiss_index") -> None:
        """Save the current FAISS vector store to disk."""
        if self.vector_store is None:
            raise RuntimeError("Vector store has not been created.")

        try:
            self.vector_store.save_local(path)
        except Exception as exc:
            raise RuntimeError(f"Failed to save FAISS vector store to {path}: {exc}") from exc

    def load_vectorstore(self, path: str = "faiss_index") -> FAISS:
        """Load a saved FAISS vector store from disk."""
        try:
            self.vector_store = FAISS.load_local(
                path,
                self.embedding_model,
                allow_dangerous_deserialization=True,
            )
            return self.vector_store
        except Exception as exc:
            raise RuntimeError(f"Failed to load FAISS vector store from {path}: {exc}") from exc

    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Return the top k most similar documents for the query."""
        if self.vector_store is None:
            raise RuntimeError("Vector store is not initialized.")

        try:
            return self.vector_store.similarity_search(query, k=k)
        except Exception as exc:
            raise RuntimeError(f"Failed to perform similarity search: {exc}") from exc
