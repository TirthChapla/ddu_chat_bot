"""
Document Management Service
Handles document uploading, deletion, and vector store synchronization.
"""

import os
import shutil
import logging
from typing import TYPE_CHECKING, Dict, Any, List
from fastapi import UploadFile

from ..config import settings
from scraper.ddu_scraper import DDUScraper

if TYPE_CHECKING:
    from embeddings.indexer import ChromaIndexer

logger = logging.getLogger(__name__)


class DocumentService:
    def __init__(self, indexer: "ChromaIndexer"):
        self.indexer = indexer
        self.uploads_dir = settings.UPLOADS_DIR
        os.makedirs(self.uploads_dir, exist_ok=True)

    async def save_and_ingest_file(self, file: UploadFile) -> Dict[str, Any]:
        """Saves an uploaded PDF/TXT/MD file and ingests it into ChromaDB."""
        filename = file.filename
        safe_filename = os.path.basename(filename)
        dest_path = os.path.join(self.uploads_dir, safe_filename)

        try:
            with open(dest_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            logger.info(f"File saved to {dest_path}. Starting ingestion...")
            result = self.indexer.ingest_single_file(dest_path)
            return result
        except Exception as e:
            logger.error(f"Failed to save and ingest {filename}: {e}")
            return {"success": False, "error": str(e), "filename": filename}

    def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Removes a document from the Chroma vector store and disk."""
        return self.indexer.delete_document_by_id(doc_id=doc_id, delete_file=True)

    def reindex_all(self) -> Dict[str, Any]:
        """Rebuilds the entire Chroma vector database from all data files."""
        return self.indexer.rebuild_index()

    def run_live_scraper_and_sync(self) -> Dict[str, Any]:
        """Runs the live web scraper against ddu.ac.in and updates ChromaDB."""
        scraper = DDUScraper(output_dir=settings.DATA_DIR)
        scrape_stats = scraper.run_scraper()
        index_stats = self.indexer.rebuild_index()
        return {
            "scrape_stats": scrape_stats,
            "index_stats": index_stats,
        }

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on all documents and categories."""
        return self.indexer.get_stats()
