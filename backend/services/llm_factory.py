"""
LLM Factory Module
Provides multi-provider LLM support: Google Gemini (Free Tier), Ollama, or an intelligent extractive synthesis engine.
"""

import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from ..config import settings

logger = logging.getLogger(__name__)


class GeminiRequestError(RuntimeError):
    """A Gemini client or generation failure that should reach the API layer."""


def reload_env():
    """Reloads .env to pick up any newly added API keys."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)


def get_llm():
    """Create a configured Gemini client without making a network request."""
    reload_env()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL).strip()

    if not gemini_key:
        logger.error("Gemini configuration invalid: GEMINI_API_KEY is missing")
        raise ValueError("GEMINI_API_KEY is not set in the environment.")

    logger.info(
        "Gemini configuration loaded: key_present=%s key_prefix=%s model=%s timeout=%ss",
        True,
        gemini_key[:10],
        model_name,
        settings.GEMINI_TIMEOUT_SECONDS,
    )
    started = time.perf_counter()
    logger.info("START Gemini client initialization; no API request has been made yet")
    
    # Configure environment to use REST transport instead of gRPC which can be slow on Windows
    os.environ["GOOGLE_API_USE_REST"] = "1"

    try:
        from langchain_google_genai import ChatGoogleGenerativeAI

        client = ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=gemini_key,
            temperature=0.2,
            top_p=0.85,
            timeout=settings.GEMINI_TIMEOUT_SECONDS,
            max_retries=0,
        )
    except Exception as exc:
        logger.exception("Gemini client initialization failed for model=%s", model_name)
        raise GeminiRequestError(f"Could not initialize Gemini model {model_name!r}.") from exc

    logger.info("DONE Gemini client initialization in %.2fs", time.perf_counter() - started)
    return client
