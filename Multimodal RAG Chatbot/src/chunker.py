"""Text chunking utilities for multimodal RAG."""

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class TextChunker:
    """Chunk documents into smaller LangChain Document objects."""

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
        )

    def chunk_documents(self, documents):
        """Convert raw documents into LangChain Document chunks.

        Args:
            documents (list): List of dicts with keys 'content', 'source', and 'page'.

        Returns:
            list[Document]: List of chunked LangChain Document objects.
        """
        if not isinstance(documents, list):
            raise ValueError("documents must be a list of document dictionaries.")

        langchain_docs = []
        for idx, document in enumerate(documents):
            if not isinstance(document, dict):
                raise ValueError(f"Document at index {idx} must be a dict.")
            if "content" not in document:
                raise ValueError(f"Document at index {idx} is missing 'content'.")

            metadata = {
                "source": document.get("source"),
                "page": document.get("page"),
            }
            langchain_docs.append(
                Document(page_content=document["content"], metadata=metadata)
            )

        try:
            chunked_documents = self.splitter.split_documents(langchain_docs)
        except Exception as exc:
            raise RuntimeError(f"Failed to chunk documents: {exc}") from exc

        return chunked_documents
