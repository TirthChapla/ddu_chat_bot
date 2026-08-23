"""
Vector Indexer Module
Manages Embedding generation and ChromaDB persistent storage.
Supports document indexing, incremental upload insertion, deletion, and similarity retrieval.
"""

import os
import glob
import logging
from typing import List, Dict, Any, Optional, Tuple

import chromadb
from chromadb.config import Settings
from langchain_core.documents import Document
from langchain_community.vectorstores import Chroma

from .loader import DocumentLoader, infer_category_from_filename
from .chunker import DocumentChunker

logger = logging.getLogger(__name__)


def get_embedding_function():
    """Initializes the embedding model based on environment configuration."""
    provider = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "")

    if provider == "gemini" and gemini_key:
        try:
            from langchain_google_genai import GoogleGenerativeAIEmbeddings
            logger.info("Using Google Generative AI Embeddings")
            return GoogleGenerativeAIEmbeddings(
                model="models/embedding-001",
                google_api_key=gemini_key
            )
        except Exception as e:
            logger.warning(f"Failed to load Google Embeddings, falling back to local: {e}")

    try:
        from langchain_huggingface import HuggingFaceEmbeddings
        model_name = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
        logger.info(f"Using HuggingFace Embeddings: {model_name}")
        return HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )
    except Exception as e:
        logger.error(f"Error initializing HuggingFace embeddings: {e}")
        # Return fallback embedding if needed
        from langchain_community.embeddings import FakeEmbeddings
        logger.warning("Using FakeEmbeddings as fallback")
        return FakeEmbeddings(size=384)


class ChromaIndexer:
    def __init__(
        self,
        persist_dir: str = "./vectordb",
        collection_name: str = "ddu_knowledge_base",
        data_dir: str = "./data",
        uploads_dir: str = "./data/raw_uploads",
    ):
        self.persist_dir = persist_dir
        self.collection_name = collection_name
        self.data_dir = data_dir
        self.uploads_dir = uploads_dir
        os.makedirs(self.persist_dir, exist_ok=True)
        os.makedirs(self.uploads_dir, exist_ok=True)

        self.embeddings = get_embedding_function()
        self.loader = DocumentLoader(data_dir=self.data_dir, uploads_dir=self.uploads_dir)
        self.chunker = DocumentChunker(
            chunk_size=int(os.getenv("CHUNK_SIZE", 800)),
            chunk_overlap=int(os.getenv("CHUNK_OVERLAP", 150))
        )
        self._init_vectorstore()

    def _init_vectorstore(self):
        """Initializes the persistent Chroma vector store."""
        self.chroma_client = chromadb.PersistentClient(path=self.persist_dir)
        self.vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=self.collection_name,
            embedding_function=self.embeddings,
        )

    def rebuild_index(self) -> Dict[str, Any]:
        """Re-indexes all documents from data/ and data/raw_uploads/ from scratch."""
        logger.info("Rebuilding ChromaDB knowledge base index...")
        try:
            # Delete existing collection to avoid duplicates
            self.chroma_client.delete_collection(self.collection_name)
        except Exception:
            pass

        self._init_vectorstore()
        raw_docs = self.loader.load_all_documents()
        chunks = self.chunker.chunk_documents(raw_docs)

        if chunks:
            self.vectorstore.add_documents(chunks)
            logger.info(f"Indexed {len(chunks)} chunks across {len(raw_docs)} documents.")

        return self.get_stats()

    def ingest_single_file(self, file_path: str) -> Dict[str, Any]:
        """Processes and adds a single uploaded file to the Chroma index."""
        ext = os.path.splitext(file_path)[1].lower()
        if ext in [".txt", ".md"]:
            docs = self.loader.load_text_file(file_path)
        elif ext == ".pdf":
            docs = self.loader.load_pdf_file(file_path)
        else:
            return {"success": False, "error": f"Unsupported file type: {ext}"}

        if not docs:
            return {"success": False, "error": "No extractable text found in file."}

        doc_id = docs[0].metadata.get("doc_id")
        # Remove any previous version of this document first
        self.delete_document_by_id(doc_id, delete_file=False)

        chunks = self.chunker.chunk_documents(docs)
        if chunks:
            self.vectorstore.add_documents(chunks)

        return {
            "success": True,
            "doc_id": doc_id,
            "filename": os.path.basename(file_path),
            "category": docs[0].metadata.get("category"),
            "chunks_added": len(chunks),
            "total_stats": self.get_stats(),
        }

    def delete_document_by_id(self, doc_id: str, delete_file: bool = True) -> Dict[str, Any]:
        """Deletes all chunks with doc_id from ChromaDB and optionally removes the file."""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            # Find matching chunk IDs
            results = collection.get(where={"doc_id": doc_id})
            ids_to_delete = results.get("ids", [])

            if ids_to_delete:
                collection.delete(ids=ids_to_delete)
                logger.info(f"Deleted {len(ids_to_delete)} chunks for doc_id: {doc_id}")

            if delete_file:
                # Check and delete from data/raw_uploads/ or data/
                for fpath in glob.glob(os.path.join(self.uploads_dir, "*.*")):
                    fname = os.path.basename(fpath)
                    if f"doc_{fname.replace('.', '_').lower()}" == doc_id:
                        try:
                            os.remove(fpath)
                            logger.info(f"Removed file from disk: {fpath}")
                        except Exception as e:
                            logger.warning(f"Could not delete physical file: {e}")

            return {"success": True, "deleted_chunks": len(ids_to_delete), "doc_id": doc_id}
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return {"success": False, "error": str(e)}

    def search(
        self,
        query: str,
        k: int = 6,
        category: Optional[str] = None,
    ) -> List[Tuple[Document, float]]:
        """
        Performs high-precision, diverse similarity search.
        Retrieves top global semantic matches and combines with category-specific chunks.
        """
        try:
            # 1. Global semantic search across entire knowledge base
            global_results = self.vectorstore.similarity_search_with_score(query=query, k=k)
            
            # 2. If category is specified, fetch category-specific matches as well
            category_results = []
            if category and category != "general":
                try:
                    category_results = self.vectorstore.similarity_search_with_score(
                        query=query,
                        k=3,
                        filter={"category": category}
                    )
                except Exception:
                    pass

            # 3. Merge and deduplicate by chunk_id / content
            seen_ids = set()
            combined = []
            
            # Prioritize top category results then global results
            for doc, score in (category_results + global_results):
                chunk_id = doc.metadata.get("chunk_id", doc.page_content[:60])
                if chunk_id not in seen_ids:
                    seen_ids.add(chunk_id)
                    combined.append((doc, score))

            # Return top k most relevant chunks
            combined.sort(key=lambda x: x[1])
            return combined[:k]
        except Exception as e:
            logger.warning(f"Search error ({e}), falling back to basic search.")
            return self.vectorstore.similarity_search_with_score(query=query, k=k)

    def get_stats(self) -> Dict[str, Any]:
        """Returns statistics on indexed documents, total chunks, and categories."""
        try:
            collection = self.chroma_client.get_collection(self.collection_name)
            total_chunks = collection.count()

            # Retrieve all metadata
            all_records = collection.get(include=["metadatas"])
            metadatas = all_records.get("metadatas", [])

            docs_map = {}
            category_counts = {}

            for m in metadatas:
                doc_id = m.get("doc_id", "unknown")
                source = m.get("source", "unknown")
                cat = m.get("category", "general")

                if doc_id not in docs_map:
                    docs_map[doc_id] = {
                        "doc_id": doc_id,
                        "source": source,
                        "category": cat,
                        "file_type": m.get("file_type", "text"),
                        "chunk_count": 0,
                    }
                docs_map[doc_id]["chunk_count"] += 1
                category_counts[cat] = category_counts.get(cat, 0) + 1

            return {
                "total_chunks": total_chunks,
                "total_documents": len(docs_map),
                "categories": category_counts,
                "documents": list(docs_map.values()),
            }
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return {
                "total_chunks": 0,
                "total_documents": 0,
                "categories": {},
                "documents": [],
            }
