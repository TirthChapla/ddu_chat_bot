"""
LLM Factory Module
Provides multi-provider LLM support: Google Gemini (Free Tier), Ollama, or an intelligent extractive synthesis engine.
"""

import os
import re
import logging
from pathlib import Path
from typing import Any, List, Optional
from dotenv import load_dotenv
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks.manager import CallbackManagerForLLMRun

logger = logging.getLogger(__name__)


def reload_env():
    """Reloads .env to pick up any newly added API keys."""
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    load_dotenv(dotenv_path=env_path, override=True)


class IntelligentExtractiveLLM(LLM):
    """
    Synthesizes direct, intelligent answers from retrieved context
    when no external cloud API key is configured.
    """
    @property
    def _llm_type(self) -> str:
        return "intelligent_extractive"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        context_match = re.search(r"Context:\s*(.*?)\s*User Question:", prompt, re.DOTALL | re.IGNORECASE)
        question_match = re.search(r"User Question:\s*(.*?)(?:\n\nHelpful|\Z)", prompt, re.DOTALL | re.IGNORECASE)

        context = context_match.group(1).strip() if context_match else prompt
        question = question_match.group(1).strip() if question_match else ""

        if not context or "No relevant information found" in context:
            return (
                "I could not find specific verified records regarding this query in the official DDU knowledge base. "
                "Please check the official university portal at https://www.ddu.ac.in or contact the DDU office."
            )

        # Extract words from question for relevance scoring
        q_words = set(re.findall(r'\w+', question.lower())) - {
            "what", "is", "the", "are", "how", "can", "to", "in", "for", "at", "ddu", "of", "and", "a", "an", "do", "does"
        }

        # Split context into semantic lines / bullet points
        raw_lines = [line.strip() for line in context.split("\n") if line.strip()]
        scored_lines = []

        for line in raw_lines:
            if line.startswith("[Source:") or line.startswith("---") or line.startswith("==="):
                continue
            line_clean = line.lower()
            overlap = sum(1 for w in q_words if w in line_clean)
            if overlap > 0 or line.startswith("-") or line.startswith("•") or line.startswith("##"):
                scored_lines.append((overlap, line))

        # Sort by overlap
        scored_lines.sort(key=lambda x: x[0], reverse=True)
        top_lines = [line for score, line in scored_lines if score > 0]

        if top_lines:
            cleaned_bullets = [re.sub(r'^[-•#*]+\s*', '', l) for l in top_lines[:5]]
            bullet_points = "\n".join([f"• {b}" for b in cleaned_bullets])
            return (
                f"**Summary of DDU Academic Guidelines & Records:**\n\n"
                f"{bullet_points}\n\n"
                f"*(Add your free `GEMINI_API_KEY` in `.env` for full natural language AI answers)*"
            )

        # Fallback to top clean paragraphs
        paragraphs = [p.strip() for p in context.split("\n\n") if not p.startswith("[Source:") and len(p.strip()) > 30]
        summary = "\n\n".join(paragraphs[:2]) if paragraphs else context[:600]
        return summary


def get_llm():
    """Dynamically returns the best available LLM based on current .env."""
    reload_env()
    provider = os.getenv("LLM_PROVIDER", "gemini").lower()
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()

    # 1. Google Gemini (Preferred & Free)
    if gemini_key:
        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            model_name = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
            logger.info(f"Initializing Google Gemini ({model_name})...")
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=gemini_key,
                temperature=0.2,
                top_p=0.85,
            )
        except Exception as e:
            logger.warning(f"Error initializing ChatGoogleGenerativeAI: {e}")

    # 2. Ollama
    if provider == "ollama":
        try:
            from langchain_community.llms import Ollama
            ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
            ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
            logger.info(f"Initializing Ollama ({ollama_model})...")
            return Ollama(
                base_url=ollama_url,
                model=ollama_model,
                temperature=0.2,
            )
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")

    # 3. Intelligent Extractive Fallback
    logger.info("Using Intelligent Extractive Context synthesis engine")
    return IntelligentExtractiveLLM()
