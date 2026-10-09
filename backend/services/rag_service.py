"""
RAG Service Module
Coordinates Query Classification, Vector Retrieval, Prompt Construction, LLM Inference,
and Source Citation extraction for Dharmsinh Desai University (DDU).
"""

import time
import datetime
import logging
from typing import TYPE_CHECKING
from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate

from ..config import settings
from ..models.schemas import ChatRequest, ChatResponse, SourceCitation, QueryLog
from .classifier_service import QueryClassifierService
from .suggestion_service import SuggestionService
from .llm_factory import GeminiRequestError, get_llm

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from embeddings.indexer import ChromaIndexer

STRICT_RAG_PROMPT_TEMPLATE = """You are the intelligent DDU AI Assistant for Dharmsinh Desai University (Nadiad, Gujarat).
Your objective is to provide direct, precise, clear, and highly useful answers to students, faculty, and applicants based on the verified university records provided below.

Guidelines for Maximum Efficiency & Quality:
1. Answer the user's question directly in the very first sentence without generic filler introductions.
2. Structure your answer using clear Markdown:
   - Use bold text for key facts, numbers, percentages, cutoffs, and deadlines.
   - Use concise bullet points or numbered steps for multi-part rules or procedures.
   - Use tables when comparing branches, fees, packages, or grading scales.
3. Be comprehensive yet concise: cover all aspects asked by the user while eliminating repetitive fluff.
4. If the provided context does not contain the answer, do not hallucinate. Instead, politely reply that you do not have the information in your current records and suggest they contact the relevant DDU office or check the official website.
5. NEVER mention the source file name, page number, or category in your response.

Context:
{context}

User Question: {question}

Direct, Accurate & Structured Answer:"""


class RAGService:
    def __init__(
        self,
        indexer: "ChromaIndexer",
        suggestion_service: SuggestionService,
    ):
        self.indexer = indexer
        self.suggestion_service = suggestion_service
        # The provider may download/configure a client and may require an API key.
        # Create it only when a chat request actually needs generation.
        self.prompt = PromptTemplate(
            template=STRICT_RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question"],
        )
        self.query_logs: List[Dict[str, Any]] = []

    def answer_query(self, request: ChatRequest) -> ChatResponse:
        request_started = time.perf_counter()
        logger.info("CHAT REQUEST START query_length=%d", len(request.query or ""))
        try:
            return self._answer_query(request)
        finally:
            logger.info(
                "CHAT REQUEST END duration=%.2fs",
                time.perf_counter() - request_started,
            )

    def _answer_query(self, request: ChatRequest) -> ChatResponse:
        """Processes a chat request through the full RAG pipeline."""
        start_time = time.perf_counter()
        query = request.query.strip()

        # 1. Query Intent & Category Classification
        category, confidence_score = QueryClassifierService.classify_query(
            query=query,
            explicit_category=request.category
        )

        # 2. Similarity Search in ChromaDB
        search_results = self.indexer.search(
            query=query,
            k=4,
            category=category if category != "general" else None,
        )

        # 3. Assemble Context & Citations
        context_parts = []
        citations: List[SourceCitation] = []
        seen_chunks = set()

        for doc, score in search_results:
            chunk_id = doc.metadata.get("chunk_id", "")
            if chunk_id in seen_chunks:
                continue
            seen_chunks.add(chunk_id)

            source_name = doc.metadata.get("source", "DDU Knowledge Base")
            page_num = doc.metadata.get("page", 1)
            cat = doc.metadata.get("category", category)

            context_parts.append(
                f"{doc.page_content}"
            )

            # Similarity score normalized (Chroma returns distance, lower is closer)
            normalized_score = max(0.0, min(1.0, 1.0 - (score if score < 1.0 else 0.5)))

            citations.append(
                SourceCitation(
                    doc_id=doc.metadata.get("doc_id", "doc_general"),
                    source=source_name,
                    category=cat,
                    page=page_num,
                    snippet=doc.page_content[:280] + ("..." if len(doc.page_content) > 280 else ""),
                    similarity_score=round(normalized_score, 3),
                )
            )

        context_str = "\n\n---\n\n".join(context_parts) if context_parts else "No relevant information found in knowledge base."

        # 4. LLM Generation
        llm_started = time.perf_counter()
        logger.info(
            "GEMINI CALL PREPARE category=%s sources=%d prompt_chars=%d",
            category,
            len(citations),
            len(context_str) + len(query),
        )
        try:
            active_llm = get_llm()
            formatted_prompt = self.prompt.format(context=context_str, question=query)
            logger.info("GEMINI CALL START model client ready; invoking generate_content")
            llm_response = active_llm.invoke(formatted_prompt)
            logger.info(
                "GEMINI CALL END duration=%.2fs response_type=%s",
                time.perf_counter() - llm_started,
                type(llm_response).__name__,
            )

            # Support both string and structured content blocks
            if hasattr(llm_response, "content"):
                if isinstance(llm_response.content, list):
                    text_blocks = [b.get("text", "") if isinstance(b, dict) else str(b) for b in llm_response.content]
                    answer_text = "".join(text_blocks)
                else:
                    answer_text = str(llm_response.content)
            else:
                answer_text = str(llm_response)
        except Exception as exc:
            logger.exception(
                "GEMINI CALL FAILED after %.2fs",
                time.perf_counter() - llm_started,
            )
            raise GeminiRequestError(
                "Gemini did not return a response. Check the API key, model name, quota, "
                "network connectivity, and timeout logs."
            ) from exc

        # 5. Dynamic Follow-Up Suggestions
        follow_ups = self.suggestion_service.get_dynamic_follow_ups(category=category, query=query)

        # 6. Metrics & Logging
        latency = round((time.perf_counter() - start_time) * 1000, 2)
        confidence_level = "High" if citations and citations[0].similarity_score > 0.6 else "Medium"

        self.query_logs.append({
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "category": category,
            "latency_ms": latency,
            "sources_count": len(citations),
        })

        return ChatResponse(
            query=query,
            answer=answer_text.strip(),
            category=category,
            sources=citations,
            follow_up_suggestions=follow_ups,
            latency_ms=latency,
            confidence=confidence_level,
        )

    def get_query_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """Returns recent query execution logs."""
        return self.query_logs[-limit:][::-1]
