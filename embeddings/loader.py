"""
Document Loader Module
Loads text, markdown, and PDF files from data/ and data/raw_uploads/ with metadata extraction.
"""

import os
import glob
from typing import List, Dict, Any
from langchain_core.documents import Document
from pypdf import PdfReader


def infer_category_from_filename(filename: str) -> str:
    """Infers the category tag based on filename keywords."""
    lower = filename.lower()
    if "admission" in lower or "acpc" in lower or "cutoff" in lower:
        return "admissions"
    elif "attend" in lower or "condonation" in lower:
        return "attendance"
    elif "place" in lower or "tpo" in lower or "intern" in lower or "recruit" in lower:
        return "placements"
    elif "exam" in lower or "spi" in lower or "cpi" in lower or "backlog" in lower or "grade" in lower:
        return "examinations"
    elif "fee" in lower or "scholarship" in lower or "mysy" in lower or "freeship" in lower:
        return "fees_scholarships"
    elif "hostel" in lower or "mess" in lower or "facility" in lower or "campus" in lower:
        return "hostel"
    elif "dept" in lower or "department" in lower or "course" in lower or "syllabus" in lower or "faculty" in lower:
        return "departments"
    elif "circular" in lower or "notice" in lower or "calendar" in lower or "faq" in lower:
        return "circulars_faqs"
    return "general"


class DocumentLoader:
    def __init__(self, data_dir: str = "./data", uploads_dir: str = "./data/raw_uploads"):
        self.data_dir = data_dir
        self.uploads_dir = uploads_dir

    def load_text_file(self, file_path: str) -> List[Document]:
        """Loads a single .txt or .md file."""
        filename = os.path.basename(file_path)
        doc_id = f"doc_{filename.replace('.', '_').lower()}"
        category = infer_category_from_filename(filename)

        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            content = f.read()

        if not content.strip():
            return []

        return [
            Document(
                page_content=content,
                metadata={
                    "doc_id": doc_id,
                    "source": filename,
                    "file_path": file_path,
                    "category": category,
                    "page": 1,
                    "file_type": "text",
                },
            )
        ]

    def load_pdf_file(self, file_path: str) -> List[Document]:
        """Loads a single .pdf file, extracting text page by page."""
        filename = os.path.basename(file_path)
        doc_id = f"doc_{filename.replace('.', '_').lower()}"
        category = infer_category_from_filename(filename)
        docs = []

        try:
            reader = PdfReader(file_path)
            for idx, page in enumerate(reader.pages):
                text = page.extract_text()
                if text and text.strip():
                    docs.append(
                        Document(
                            page_content=text.strip(),
                            metadata={
                                "doc_id": doc_id,
                                "source": filename,
                                "file_path": file_path,
                                "category": category,
                                "page": idx + 1,
                                "total_pages": len(reader.pages),
                                "file_type": "pdf",
                            },
                        )
                    )
        except Exception as e:
            print(f"Error reading PDF {file_path}: {e}")

        return docs

    def load_all_documents(self) -> List[Document]:
        """Loads all documents from data/ and data/raw_uploads/."""
        all_docs = []

        # 1. Text and markdown files in data/
        for ext in ["*.txt", "*.md"]:
            for fpath in glob.glob(os.path.join(self.data_dir, ext)):
                all_docs.extend(self.load_text_file(fpath))

        # 2. Uploaded documents in data/raw_uploads/
        if os.path.exists(self.uploads_dir):
            for fpath in glob.glob(os.path.join(self.uploads_dir, "*.*")):
                ext = os.path.splitext(fpath)[1].lower()
                if ext in [".txt", ".md"]:
                    all_docs.extend(self.load_text_file(fpath))
                elif ext == ".pdf":
                    all_docs.extend(self.load_pdf_file(fpath))

        return all_docs
