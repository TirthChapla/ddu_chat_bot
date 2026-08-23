"""
Suggestions Router
Endpoints: /api/suggestions, /api/suggestions/category/{category_id}
"""

from fastapi import APIRouter, Depends
from ..models.schemas import SuggestionsResponse, SubTopic
from typing import List

router = APIRouter(prefix="/suggestions", tags=["Suggestions"])


def get_suggestion_service():
    from ..main import suggestion_service
    return suggestion_service


@router.get("", response_model=SuggestionsResponse)
async def get_all_suggestions(service = Depends(get_suggestion_service)):
    """Returns primary categories, welcome message, and subtopics for guided navigation."""
    return service.get_welcome_suggestions()


@router.get("/category/{category_id}", response_model=List[SubTopic])
async def get_category_subtopics(category_id: str, service = Depends(get_suggestion_service)):
    """Returns guided subtopics for a specific category."""
    return service.get_subtopics_for_category(category_id)
