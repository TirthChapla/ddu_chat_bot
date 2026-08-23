import os
import pytest
from embeddings.loader import DocumentLoader, infer_category_from_filename
from embeddings.chunker import DocumentChunker
from langchain_core.documents import Document


def test_infer_category():
    assert infer_category_from_filename("attendance_rules.txt") == "attendance"
    assert infer_category_from_filename("placement_stats.txt") == "placements"
    assert infer_category_from_filename("admissions.txt") == "admissions"
    assert infer_category_from_filename("fee_structure.txt") == "fees_scholarships"
    assert infer_category_from_filename("examination_rules.txt") == "examinations"


def test_document_loader(tmp_path):
    # Create sample file
    test_file = tmp_path / "test_attendance.txt"
    test_file.write_text("DDU requires 75% minimum attendance for all engineering students.", encoding="utf-8")
    
    loader = DocumentLoader(data_dir=str(tmp_path), uploads_dir=str(tmp_path / "uploads"))
    docs = loader.load_text_file(str(test_file))
    
    assert len(docs) == 1
    assert "75%" in docs[0].page_content
    assert docs[0].metadata["category"] == "attendance"
    assert docs[0].metadata["source"] == "test_attendance.txt"


def test_chunker():
    doc = Document(
        page_content="Header 1\n\n" + ("This is detailed text content for DDU university regulations. " * 30),
        metadata={"doc_id": "doc_test", "source": "test.txt", "category": "general"}
    )
    chunker = DocumentChunker(chunk_size=200, chunk_overlap=50)
    chunks = chunker.chunk_documents([doc])
    
    assert len(chunks) > 1
    for c in chunks:
        assert "chunk_id" in c.metadata
        assert c.metadata["doc_id"] == "doc_test"
