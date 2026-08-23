import os
import pytest
from embeddings.indexer import ChromaIndexer


def test_chroma_indexer_stats(tmp_path):
    persist_dir = str(tmp_path / "vectordb")
    data_dir = str(tmp_path / "data")
    uploads_dir = str(tmp_path / "uploads")
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(uploads_dir, exist_ok=True)

    # Write a test file
    with open(os.path.join(data_dir, "test_admission.txt"), "w", encoding="utf-8") as f:
        f.write("# DDU Admissions\nEligibility for B.Tech requires 50% in 12th Board PCM and valid GUJCET/JEE score.")

    indexer = ChromaIndexer(
        persist_dir=persist_dir,
        collection_name="test_collection",
        data_dir=data_dir,
        uploads_dir=uploads_dir
    )
    
    stats = indexer.rebuild_index()
    assert stats["total_chunks"] >= 1
    assert stats["total_documents"] >= 1

    # Ingest another file into uploads
    upload_file = os.path.join(uploads_dir, "placement_doc.txt")
    with open(upload_file, "w", encoding="utf-8") as f:
        f.write("# Placement FAQs\nStudents with more than 1 active backlog cannot sit for placement drives.")

    res = indexer.ingest_single_file(upload_file)
    assert res["success"] is True
    assert res["chunks_added"] >= 1
    assert res["category"] == "placements"

    # Search
    search_res = indexer.search("backlog rules for placement", k=2)
    assert len(search_res) >= 1
    assert "backlog" in search_res[0][0].page_content.lower()

    # Delete
    del_res = indexer.delete_document_by_id(res["doc_id"])
    assert del_res["success"] is True
