"""
Text Chunker Module
Splits loaded documents into semantic chunks with attached metadata.
"""

from typing import List
from langchain_core.documents import Document


class _RecursiveCharacterSplitter:
    def __init__(self, chunk_size: int, chunk_overlap: int, separators: List[str]):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = separators

    def split_text(self, text: str) -> List[str]:
        pieces = self._split(text, self.separators)
        chunks = []
        current = ""

        for piece in pieces:
            if len(current) + len(piece) <= self.chunk_size:
                current += piece
                continue

            if current:
                chunks.append(current)
                overlap = current[-self.chunk_overlap:] if self.chunk_overlap else ""
                current = overlap + piece
            else:
                chunks.append(piece[:self.chunk_size])
                current = piece[self.chunk_size - self.chunk_overlap:]

        if current:
            chunks.append(current)

        return chunks

    def _split(self, text: str, separators: List[str]) -> List[str]:
        if len(text) <= self.chunk_size:
            return [text]

        separator = separators[-1]
        remaining_separators = []
        for index, candidate in enumerate(separators):
            if candidate == "" or candidate in text:
                separator = candidate
                remaining_separators = separators[index + 1:]
                break

        if separator == "":
            return [text[index:index + self.chunk_size] for index in range(0, len(text), self.chunk_size)]

        raw_parts = text.split(separator)
        parts = [raw_parts[0]]
        parts.extend(separator + part for part in raw_parts[1:])
        result = []
        for part in parts:
            if len(part) > self.chunk_size and remaining_separators:
                result.extend(self._split(part, remaining_separators))
            else:
                result.append(part)
        return result


class DocumentChunker:
    def __init__(self, chunk_size: int = 800, chunk_overlap: int = 150):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.splitter = _RecursiveCharacterSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " ", ""],
        )

    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Splits a list of documents into chunked Document objects with unique chunk_id metadata."""
        chunked_docs = []
        doc_chunk_counters = {}

        for doc in documents:
            chunks = [
                Document(page_content=content, metadata=dict(doc.metadata))
                for content in self.splitter.split_text(doc.page_content)
            ]
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
