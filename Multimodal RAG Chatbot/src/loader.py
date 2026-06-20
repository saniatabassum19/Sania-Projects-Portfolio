"""Document loading utilities for multimodal RAG."""

import os
import tempfile
from pathlib import Path

import fitz
import easyocr
import pandas as pd


class DocumentLoader:
    def __init__(self):
        self.ocr_reader = easyocr.Reader(["en"], gpu=False)

    def _get_filename(self, file):
        if hasattr(file, "name"):
            return Path(file.name).name
        return None

    def load_pdf(self, file):
        documents = []
        filename = self._get_filename(file) or "unknown.pdf"

        try:
            if hasattr(file, "seek"):
                file.seek(0)
            pdf_bytes = file.read() if hasattr(file, "read") else None
            if pdf_bytes is None:
                raise ValueError("PDF file object is not readable.")

            with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
                for page_number in range(doc.page_count):
                    page = doc.load_page(page_number)
                    extracted_text = page.get_text("text").strip()
                    documents.append(
                        {
                            "content": extracted_text,
                            "source": filename,
                            "page": page_number + 1,
                        }
                    )
        except Exception as exc:
            raise RuntimeError(f"Failed to load PDF {filename}: {exc}") from exc

        return documents

    def load_image(self, file):
        filename = self._get_filename(file) or "unknown_image"

        try:
            if hasattr(file, "seek"):
                file.seek(0)
            image_bytes = file.read() if hasattr(file, "read") else None
            if image_bytes is None:
                raise ValueError("Image file object is not readable.")

            suffix = Path(filename).suffix or ".png"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as temp_file:
                temp_file.write(image_bytes)
                temp_path = temp_file.name

            try:
                result = self.ocr_reader.readtext(temp_path, detail=0)
            finally:
                os.unlink(temp_path)

            extracted_text = "\n".join(result).strip()

            return [
                {
                    "content": extracted_text,
                    "source": filename,
                    "page": None,
                }
            ]
        except Exception as exc:
            raise RuntimeError(f"Failed to load image {filename}: {exc}") from exc

    def load_csv(self, file):
        filename = self._get_filename(file) or "unknown.csv"

        try:
            if hasattr(file, "seek"):
                file.seek(0)
            df = pd.read_csv(file)
            rows = []
            for _, row in df.iterrows():
                row_text = "; ".join(
                    f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])
                )
                rows.append(row_text)

            content = "\n".join(rows).strip()
            return [
                {
                    "content": content,
                    "source": filename,
                    "page": None,
                }
            ]
        except Exception as exc:
            raise RuntimeError(f"Failed to load CSV {filename}: {exc}") from exc

    def load_excel(self, file):
        filename = self._get_filename(file) or "unknown.xlsx"

        try:
            if hasattr(file, "seek"):
                file.seek(0)
            excel_data = pd.read_excel(file, sheet_name=None)
            documents = []

            for sheet_name, df in excel_data.items():
                rows = []
                for _, row in df.iterrows():
                    row_text = "; ".join(
                        f"{col}: {row[col]}" for col in df.columns if pd.notna(row[col])
                    )
                    rows.append(row_text)

                content = f"Sheet: {sheet_name}\n" + "\n".join(rows)
                documents.append(
                    {
                        "content": content.strip(),
                        "source": filename,
                        "page": None,
                    }
                )

            return documents
        except Exception as exc:
            raise RuntimeError(f"Failed to load Excel {filename}: {exc}") from exc

    def load_file(self, file):
        """Load a file based on its extension."""
        filename = self._get_filename(file) or ""
        ext = Path(filename).suffix.lower()

        if ext == ".pdf":
            return self.load_pdf(file)
        if ext in {".png", ".jpg", ".jpeg"}:
            return self.load_image(file)
        if ext == ".csv":
            return self.load_csv(file)
        if ext == ".xlsx":
            return self.load_excel(file)

        raise ValueError(f"Unsupported file type: {ext or filename}")
