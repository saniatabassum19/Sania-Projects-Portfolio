"""Retriever utilities for multimodal RAG."""

from typing import List

from langchain_core.documents import Document


class RetrieverManager:
    """Manage retrieval operations against a FAISS vector store."""

    def __init__(self, vector_store):
        self.vector_store = vector_store

    def get_retriever(self, k: int = 4):
        """Return a retriever configured for similarity search."""
        if self.vector_store is None:
            raise RuntimeError("Vector store is not initialized.")

        try:
            return self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": k},
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to create retriever: {exc}") from exc

    def retrieve(self, query: str, k: int = 4) -> List[Document]:
        """Retrieve the top k relevant documents for a query."""
        if not query:
            raise ValueError("Query must be a non-empty string.")

        retriever = self.get_retriever(k=k)

        try:
            if hasattr(retriever, "invoke"):
                documents = retriever.invoke(query)
            else:
                documents = retriever.get_relevant_documents(query)
            if not isinstance(documents, list):
                raise RuntimeError("Retriever returned an unexpected result type.")
            return documents
        except Exception as exc:
            raise RuntimeError(f"Failed to retrieve documents: {exc}") from exc
