"""
Chat Router
Endpoint: /api/chat
"""

import asyncio
import logging

from fastapi import APIRouter, Depends, HTTPException
from ..models.schemas import ChatRequest, ChatResponse
from ..services.llm_factory import GeminiRequestError

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/chat", tags=["Chat"])

# Service dependency injected from main app state
def get_rag_service():
    from ..main import rag_service
    return rag_service


@router.post("", response_model=ChatResponse)
async def handle_chat(
    request: ChatRequest,
    service = Depends(get_rag_service)
):
    """Processes user queries through the RAG pipeline."""
    if not request.query or not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")
    
    try:
        response = await asyncio.wait_for(
            asyncio.to_thread(service.answer_query, request),
            timeout=60.0,
        )
        return response
    except asyncio.TimeoutError as exc:
        logger.exception("Chat request exceeded the 60-second API timeout")
        raise HTTPException(
            status_code=504,
            detail="Gemini took too long to respond. Please try again later.",
        ) from exc
    except GeminiRequestError as exc:
        logger.exception("Gemini request failed")
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as e:
        logger.exception("Unexpected chat request failure")
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
