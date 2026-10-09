"""
Application Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from workspace root
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    PROJECT_NAME: str = "DDU AI Assistant"
    VERSION: str = "1.0.0"
    API_PREFIX: str = "/api"

    # LLM Settings
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini").lower()
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    GEMINI_TIMEOUT_SECONDS: float = float(os.getenv("GEMINI_TIMEOUT_SECONDS", "60"))
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

    # Embeddings & Vector DB
    EMBEDDING_PROVIDER: str = os.getenv("EMBEDDING_PROVIDER", "local").lower()
    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")
    CHROMA_PERSIST_DIR: str = os.getenv("CHROMA_PERSIST_DIR", "./vectordb")
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "ddu_knowledge_base")

    # Data directories
    DATA_DIR: str = str(Path(__file__).resolve().parent.parent / "data")
    UPLOADS_DIR: str = str(Path(__file__).resolve().parent.parent / "data" / "raw_uploads")
    SUGGESTIONS_CONFIG_PATH: str = str(Path(__file__).resolve().parent.parent / "data" / "suggestions_config.json")

    # Chunking
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", "800"))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", "150"))

    # Server
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))


settings = Settings()
