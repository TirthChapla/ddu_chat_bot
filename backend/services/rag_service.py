"""
RAG Service Module
Coordinates Query Classification, Vector Retrieval, Prompt Construction, LLM Inference,
and Source Citation extraction for Dharmsinh Desai University (DDU).
"""

import time
import datetime
import logging
from typing import Dict, Any, List, Optional

from langchain_core.prompts import PromptTemplate

from ..config import settings
from ..models.schemas import ChatRequest, ChatResponse, SourceCitation, QueryLog
from embeddings.indexer import ChromaIndexer
from .classifier_service import QueryClassifierService
from .suggestion_service import SuggestionService
from .llm_factory import get_llm

logger = logging.getLogger(__name__)

STRICT_RAG_PROMPT_TEMPLATE = """You are the intelligent DDU AI Assistant for Dharmsinh Desai University (Nadiad, Gujarat).
Your objective is to provide direct, precise, clear, and highly useful answers to students, faculty, and applicants based on the verified university records provided below.

Guidelines for Maximum Efficiency & Quality:
1. Answer the user's question directly in the very first sentence without generic filler introductions.
2. Structure your answer using clear Markdown:
   - Use bold text for key facts, numbers, percentages, cutoffs, and deadlines.
   - Use concise bullet points or numbered steps for multi-part rules or procedures.
   - Use tables when comparing branches, fees, packages, or grading scales.
3. Be comprehensive yet concise: cover all aspects asked by the user while eliminating repetitive fluff.
4. If specific information is not in the records, state what is known and provide the relevant DDU office contact.

Context:
{context}

User Question: {question}

Direct, Accurate & Structured Answer:"""


class RAGService:
    def __init__(
        self,
        indexer: ChromaIndexer,
        suggestion_service: SuggestionService,
    ):
        self.indexer = indexer
        self.suggestion_service = suggestion_service
        self.llm = get_llm()
        self.prompt = PromptTemplate(
            template=STRICT_RAG_PROMPT_TEMPLATE,
            input_variables=["context", "question"],
        )
        self.query_logs: List[Dict[str, Any]] = []

    def answer_query(self, request: ChatRequest) -> ChatResponse:
        """Processes a chat request through the full RAG pipeline."""
        start_time = time.time()
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
                f"[Source: {source_name}, Page: {page_num}, Category: {cat}]\n{doc.page_content}"
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
        try:
            active_llm = get_llm()
            formatted_prompt = self.prompt.format(context=context_str, question=query)
            llm_response = active_llm.invoke(formatted_prompt)
            # Support both string and structured content blocks
            if hasattr(llm_response, "content"):
                if isinstance(llm_response.content, list):
                    text_blocks = [b.get("text", "") if isinstance(b, dict) else str(b) for b in llm_response.content]
                    answer_text = "".join(text_blocks)
                else:
                    answer_text = str(llm_response.content)
            else:
                answer_text = str(llm_response)
        except Exception as e:
            logger.error(f"Error during LLM invocation: {e}")
            answer_text = (
                f"Based on DDU records:\n\n{context_parts[0] if context_parts else 'No records available.'}\n\n"
                f"*Note: For official verification, please contact the DDU office.*"
            )

        # 5. Dynamic Follow-Up Suggestions
        follow_ups = self.suggestion_service.get_dynamic_follow_ups(category=category, query=query)

        # 6. Metrics & Logging
        latency = round((time.time() - start_time) * 1000, 2)
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
