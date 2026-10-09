"""
FastAPI Backend Application Entrypoint for DDU AI Assistant
"""

import os
import logging
import importlib
import time
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Any, Callable, TypeVar
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from .config import settings
from .routes import chat_router, suggestions_router, admin_router, analytics_router

if TYPE_CHECKING:
    from embeddings.indexer import ChromaIndexer
    from .services.suggestion_service import SuggestionService
    from .services.document_service import DocumentService
    from .services.rag_service import RAGService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ddu_assistant")
T = TypeVar("T")


def _timed_step(label: str, operation: Callable[[], T]) -> T:
    """Run one startup operation with a clear boundary and duration."""
    started = time.perf_counter()
    logger.info("START %s", label)
    try:
        result = operation()
    except Exception:
        logger.exception("FAILED %s after %.2fs", label, time.perf_counter() - started)
        raise
    logger.info("DONE %s in %.2fs", label, time.perf_counter() - started)
    return result

# Shared Singletons
indexer: Any = None
suggestion_service: Any = None
document_service: Any = None
rag_service: Any = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initializes services and validates vector store index on startup."""
    global indexer, suggestion_service, document_service, rag_service
    started = time.perf_counter()
    logger.info("Starting DDU AI Assistant Backend startup")
    logger.info(
        "Configuration: host=%s port=%s embedding_provider=%s embedding_model=%s "
        "llm_provider=%s gemini_model=%s gemini_key_present=%s gemini_key_prefix=%s "
        "gemini_timeout=%ss chroma_dir=%s",
        settings.HOST,
        settings.PORT,
        settings.EMBEDDING_PROVIDER,
        settings.EMBEDDING_MODEL,
        settings.LLM_PROVIDER,
        settings.GEMINI_MODEL,
        bool(settings.GEMINI_API_KEY.strip()),
        settings.GEMINI_API_KEY.strip()[:10] if settings.GEMINI_API_KEY.strip() else "<missing>",
        settings.GEMINI_TIMEOUT_SECONDS,
        settings.CHROMA_PERSIST_DIR,
    )

    try:
        indexer_class = _timed_step(
            "import embeddings.indexer (may load LangChain/Chroma dependencies)",
            lambda: importlib.import_module("embeddings.indexer").ChromaIndexer,
        )
        suggestion_class = _timed_step(
            "import backend.services.suggestion_service",
            lambda: importlib.import_module("backend.services.suggestion_service").SuggestionService,
        )
        document_class = _timed_step(
            "import backend.services.document_service",
            lambda: importlib.import_module("backend.services.document_service").DocumentService,
        )
        rag_class = _timed_step(
            "import backend.services.rag_service",
            lambda: importlib.import_module("backend.services.rag_service").RAGService,
        )

        indexer = _timed_step(
            "construct ChromaIndexer (embedding model and vector store)",
            lambda: indexer_class(
                persist_dir=settings.CHROMA_PERSIST_DIR,
                collection_name=settings.COLLECTION_NAME,
                data_dir=settings.DATA_DIR,
                uploads_dir=settings.UPLOADS_DIR,
            ),
        )
        suggestion_service = _timed_step(
            "construct SuggestionService",
            lambda: suggestion_class(config_path=settings.SUGGESTIONS_CONFIG_PATH),
        )
        document_service = _timed_step(
            "construct DocumentService",
            lambda: document_class(indexer=indexer),
        )
        rag_service = _timed_step(
            "construct RAGService (LLM remains lazy until a chat request)",
            lambda: rag_class(indexer=indexer, suggestion_service=suggestion_service),
        )

        stats = _timed_step("read ChromaDB index statistics", indexer.get_stats)
        if stats["total_chunks"] == 0:
            logger.info("ChromaDB index is empty; starting seed document indexing")
            stats = _timed_step("rebuild ChromaDB seed index", indexer.rebuild_index)
        logger.info(
            "ChromaDB ready: %s chunks across %s documents",
            stats["total_chunks"],
            stats["total_documents"],
        )
    except Exception as exc:
        logger.exception("Backend startup failed after %.2fs", time.perf_counter() - started)
        raise RuntimeError(
            "DDU backend startup failed. See the preceding timed startup step for the exact failing operation."
        ) from exc

    logger.info("Backend startup complete in %.2fs; accepting requests", time.perf_counter() - started)

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
    logger.info("Launching Uvicorn on %s:%s", settings.HOST, settings.PORT)
    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )
