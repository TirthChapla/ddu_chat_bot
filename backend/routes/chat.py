"""
Chat Router
Endpoint: /api/chat
"""

from fastapi import APIRouter, Depends, HTTPException
from ..models.schemas import ChatRequest, ChatResponse

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
        response = service.answer_query(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating answer: {str(e)}")
