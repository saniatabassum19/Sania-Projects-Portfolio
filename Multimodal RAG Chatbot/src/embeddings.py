"""Embedding utilities for multimodal RAG."""

from langchain_community.embeddings import HuggingFaceEmbeddings


class EmbeddingModel:
    """Wrapper for HuggingFace sentence-transformer embeddings."""

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            self.model_name = model_name
            self.embeddings = HuggingFaceEmbeddings(model_name=model_name)
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize embedding model {model_name}: {exc}") from exc

    def get_embeddings_model(self):
        """Return the underlying LangChain HuggingFaceEmbeddings instance."""
        return self.embeddings

    def embed_documents(self, documents):
        """Embed a list of LangChain Document objects.

        Args:
            documents (list): List of LangChain Document objects.

        Returns:
            list[list[float]]: Embeddings for each document.
        """
        if not isinstance(documents, list):
            raise ValueError("documents must be a list of LangChain Document objects.")

        try:
            texts = [
                doc.page_content if hasattr(doc, "page_content") else str(doc)
                for doc in documents
            ]
            return self.embeddings.embed_documents(texts)
        except Exception as exc:
            raise RuntimeError(f"Failed to embed documents: {exc}") from exc
