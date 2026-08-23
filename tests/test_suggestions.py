import pytest
from backend.services.suggestion_service import SuggestionService


def test_suggestion_service():
    service = SuggestionService(config_path="./data/suggestions_config.json")
    welcome = service.get_welcome_suggestions()
    
    assert len(welcome.primary_categories) >= 5
    assert any(c.id == "admissions" for c in welcome.primary_categories)
    assert any(c.id == "attendance" for c in welcome.primary_categories)
    assert any(c.id == "placements" for c in welcome.primary_categories)


def test_dynamic_follow_ups():
    service = SuggestionService(config_path="./data/suggestions_config.json")
    follow_ups = service.get_dynamic_follow_ups(category="attendance", query="What is minimum attendance?")
    
    assert len(follow_ups) > 0
    assert isinstance(follow_ups, list)
