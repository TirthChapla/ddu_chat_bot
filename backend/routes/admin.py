"""
Admin Knowledge Base Management Router
Endpoints for uploading PDFs/TXTs, listing documents, deleting files, re-indexing, and scraping.
"""

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from typing import List, Dict, Any

from ..models.schemas import AdminStatsResponse, UploadResponse

router = APIRouter(prefix="/admin", tags=["Admin Knowledge Base"])


def get_document_service():
    from ..main import document_service
    return document_service


@router.post("/upload", response_model=UploadResponse)
async def upload_document(
    file: UploadFile = File(...),
    service = Depends(get_document_service)
):
    """Uploads a PDF, TXT, or MD document, automatically chunks, embeds, and indexes it."""
    valid_extensions = [".pdf", ".txt", ".md"]
    filename = file.filename or "uploaded_file"
    if not any(filename.lower().endswith(ext) for ext in valid_extensions):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file format. Please upload one of: {', '.join(valid_extensions)}"
        )

    result = await service.save_and_ingest_file(file)
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to ingest document."))

    return UploadResponse(
        success=True,
        doc_id=result.get("doc_id"),
        filename=filename,
        category=result.get("category"),
        chunks_added=result.get("chunks_added", 0),
        message=f"Successfully uploaded and indexed {filename} ({result.get('chunks_added', 0)} chunks)."
    )


@router.get("/stats", response_model=AdminStatsResponse)
async def get_knowledge_base_stats(service = Depends(get_document_service)):
    """Returns total chunks, document list, and category breakdown."""
    stats = service.get_stats()
    return stats


@router.delete("/documents/{doc_id}")
async def delete_document(doc_id: str, service = Depends(get_document_service)):
    """Deletes all chunks for a document from ChromaDB and deletes the file from disk."""
    result = service.delete_document(doc_id)
    if not result.get("success", False):
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to delete document."))
    return {"success": True, "message": f"Deleted document {doc_id} and cleared {result.get('deleted_chunks', 0)} vector chunks."}


@router.post("/reindex")
async def trigger_full_reindex(service = Depends(get_document_service)):
    """Rebuilds the entire Chroma vector database index from all stored files."""
    try:
        stats = service.reindex_all()
        return {"success": True, "message": "Knowledge base re-indexed successfully.", "stats": stats}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Re-indexing failed: {str(e)}")


@router.post("/scrape")
async def trigger_live_scrape(service = Depends(get_document_service)):
    """Scrapes official DDU website pages and updates ChromaDB."""
    try:
        result = service.run_live_scraper_and_sync()
        return {"success": True, "message": "Scrape and sync complete.", "details": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraper error: {str(e)}")
