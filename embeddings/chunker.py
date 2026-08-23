"""
Text Chunker Module
Splits loaded documents into semantic chunks with attached metadata.
"""

from typing import List
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
            keep_separator=True,
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Splits a list of documents into chunked Document objects with unique chunk_id metadata."""
        chunked_docs = []
        doc_chunk_counters = {}

        for doc in documents:
            chunks = self.splitter.split_documents([doc])
            doc_id = doc.metadata.get("doc_id", "unknown_doc")

            if doc_id not in doc_chunk_counters:
                doc_chunk_counters[doc_id] = 0

            for chunk in chunks:
                doc_chunk_counters[doc_id] += 1
                chunk_id = f"{doc_id}_chunk_{doc_chunk_counters[doc_id]}"

                # Enhance chunk metadata
                chunk.metadata["chunk_id"] = chunk_id
                chunk.metadata["char_count"] = len(chunk.page_content)
                chunked_docs.append(chunk)

        return chunked_docs
