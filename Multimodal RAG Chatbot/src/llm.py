"""LLM utilities for multimodal RAG."""

import os
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI


class GeminiRAG:
    """Handle context building and question answering with Gemini 2.5 Flash."""

    def __init__(self):
        env_path = Path(__file__).resolve().parents[1] / ".env"
        load_dotenv(dotenv_path=env_path)

        api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY or GEMINI_API_KEY is not set in the .env file.")

        try:
            self.model = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash",
                temperature=0.2,
                google_api_key=api_key,
            )
        except Exception as exc:
            raise RuntimeError(f"Failed to initialize Gemini model: {exc}") from exc

    def build_context(self, documents: List[Document]) -> str:
        """Build a single context string from retrieved documents."""
        if not isinstance(documents, list):
            raise ValueError("documents must be a list of LangChain Document objects.")

        context_entries = []
        for doc_idx, document in enumerate(documents):
            if not hasattr(document, "page_content"):
                raise ValueError(f"Document at index {doc_idx} is missing page_content.")

            metadata = getattr(document, "metadata", {}) or {}
            source = metadata.get("source", "unknown")
            page = metadata.get("page")

            entry_lines = [f"Source: {source}"]
            if page is not None:
                entry_lines.append(f"Page: {page}")
            entry_lines.append("Content:")
            entry_lines.append(document.page_content.strip())

            context_entries.append("\n".join(entry_lines).strip())

        return "\n---\n".join(context_entries)

    def generate_answer(self, question: str, documents: List[Document]) -> Dict[str, Optional[List[Dict[str, Optional[int]]]]]:
        """Generate an answer from Gemini using the provided documents as context."""
        if not isinstance(question, str) or not question.strip():
            raise ValueError("Question must be a non-empty string.")
        if not isinstance(documents, list):
            raise ValueError("documents must be a list of LangChain Document objects.")

        context = self.build_context(documents)
        prompt = (
            "You are a helpful AI assistant.\n\n"
            "Answer ONLY using the provided context.\n"
            "If the answer cannot be found in the context, reply exactly:\n"
            '"I couldn\'t find relevant information in the uploaded documents."\n\n'
            "Always mention:\n"
            "- Source filename\n"
            "- Page number if available\n\n"
            "Context:\n"
            f"{context}\n\n"
            "Question:\n"
            f"{question}\n\n"
            "Answer:\n"
        )

        try:
            response = self.model.invoke(prompt)
            answer = response.content if hasattr(response, "content") else str(response)
        except Exception as exc:
            raise RuntimeError(f"Failed to generate answer from Gemini: {exc}") from exc

        sources = []
        seen = set()
        for document in documents:
            metadata = getattr(document, "metadata", {}) or {}
            source = metadata.get("source", "unknown")
            page = metadata.get("page")
            key = (source, page)
            if key not in seen:
                seen.add(key)
                sources.append({"source": source, "page": page})

        return {"answer": answer, "sources": sources}
