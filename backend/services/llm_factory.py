"""Create the configured LLM provider for the RAG service."""

import os
import logging
import time
from pathlib import Path
from dotenv import load_dotenv
from ..config import settings

logger = logging.getLogger(__name__)


class LLMRequestError(RuntimeError):
    """An LLM client or generation failure that should reach the API layer."""


class GeminiRequestError(LLMRequestError):
    """Backward-compatible name for callers that expect a Gemini error."""


def reload_env():
    """Reloads .env to pick up any newly added API keys."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)


def get_llm():
    """Create a configured LLM client without making a generation request.

    Set ``LOCAL_MODEL=true`` to use a local Ollama server. Any other value
    selects Google's Gemini API.
    """
    reload_env()
    local_model = os.getenv("LOCAL_MODEL", "false").strip().lower() == "true"
    provider = "ollama" if local_model else "gemini"
    started = time.perf_counter()

    if provider == "gemini":
        gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
        model_name = os.getenv("GEMINI_MODEL", settings.GEMINI_MODEL).strip()
        if not gemini_key:
            logger.error("Gemini configuration invalid: GEMINI_API_KEY is missing")
            raise ValueError("GEMINI_API_KEY is not set in the environment.")

        logger.info(
            "Initializing LLM provider=gemini model=%s key_present=%s timeout=%ss",
            model_name,
            True,
            settings.GEMINI_TIMEOUT_SECONDS,
        )
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
    elif provider == "ollama":
        base_url = os.getenv("OLLAMA_BASE_URL", settings.OLLAMA_BASE_URL).strip()
        model_name = os.getenv("OLLAMA_MODEL", settings.OLLAMA_MODEL).strip()
        if not base_url or not model_name:
            raise ValueError("OLLAMA_BASE_URL and OLLAMA_MODEL must be set for the Ollama provider.")

        logger.info(
            "Initializing LLM provider=ollama model=%s base_url=%s timeout=%ss",
            model_name,
            base_url,
            settings.GEMINI_TIMEOUT_SECONDS,
        )
        try:
            from langchain_ollama import ChatOllama

            client = ChatOllama(
                model=model_name,
                base_url=base_url,
                temperature=0.2,
            )
        except Exception as exc:
            logger.exception(
                "Ollama client initialization failed for model=%s base_url=%s",
                model_name,
                base_url,
            )
            raise LLMRequestError(
                f"Could not initialize Ollama model {model_name!r}. "
                "Install langchain-ollama and verify that Ollama is running."
            ) from exc
    else:
        raise ValueError(
            f"Unsupported LLM_PROVIDER {provider!r}. Choose 'gemini' or 'ollama'."
        )

    logger.info(
        "LLM provider=%s client initialized in %.2fs; no generation request was made",
        provider,
        time.perf_counter() - started,
    )
    return client
