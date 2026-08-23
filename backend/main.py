"""
FastAPI Backend Application Entrypoint for DDU AI Assistant
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from embeddings.indexer import ChromaIndexer
from .services.suggestion_service import SuggestionService
from .services.document_service import DocumentService
from .services.rag_service import RAGService
from .routes import chat_router, suggestions_router, admin_router, analytics_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ddu_assistant")

# Shared Singletons
indexer: ChromaIndexer = None
suggestion_service: SuggestionService = None
document_service: DocumentService = None
rag_service: RAGService = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes services and validates vector store index on startup."""
    global indexer, suggestion_service, document_service, rag_service
    logger.info("Starting DDU AI Assistant Backend...")

    indexer = ChromaIndexer(
        persist_dir=settings.CHROMA_PERSIST_DIR,
        collection_name=settings.COLLECTION_NAME,
        data_dir=settings.DATA_DIR,
        uploads_dir=settings.UPLOADS_DIR,
    )
    suggestion_service = SuggestionService(config_path=settings.SUGGESTIONS_CONFIG_PATH)
    document_service = DocumentService(indexer=indexer)
    rag_service = RAGService(indexer=indexer, suggestion_service=suggestion_service)

    # Check if index needs building
    stats = indexer.get_stats()
    if stats["total_chunks"] == 0:
        logger.info("ChromaDB index is empty. Auto-indexing initial seed documents...")
        indexer.rebuild_index()
        logger.info("Initial index build completed.")
    else:
        logger.info(f"Loaded existing ChromaDB vector index ({stats['total_chunks']} chunks across {stats['total_documents']} documents).")

    yield
    logger.info("Shutting down DDU AI Assistant Backend...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Intelligent RAG Assistant for Dharmsinh Desai University (DDU), Nadiad",
    lifespan=lifespan,
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Routers
app.include_router(chat_router, prefix=settings.API_PREFIX)
app.include_router(suggestions_router, prefix=settings.API_PREFIX)
app.include_router(admin_router, prefix=settings.API_PREFIX)
app.include_router(analytics_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "llm_provider": settings.LLM_PROVIDER,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
    }


# Mount static frontend build if present
frontend_dist = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/", StaticFiles(directory=frontend_dist, html=True), name="frontend")
else:
    @app.get("/")
    async def root():
        """Root landing endpoint."""
        return {
            "message": "Welcome to DDU AI Assistant API",
            "docs_url": "/docs",
            "version": settings.VERSION,
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
