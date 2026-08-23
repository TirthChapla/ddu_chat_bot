"""
Suggestion Service
Provides guided taxonomy, category sub-topics, and dynamic post-answer follow-ups.
"""

import json
import os
import logging
from typing import List, Dict, Any, Optional

from ..config import settings
from ..models.schemas import SuggestionsResponse, PrimaryCategory, SubTopic

logger = logging.getLogger(__name__)


class SuggestionService:
    def __init__(self, config_path: Optional[str] = None):
        self.config_path = config_path or settings.SUGGESTIONS_CONFIG_PATH
        self._config_cache = None
        self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Loads or reloads suggestions configuration from JSON file."""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    self._config_cache = json.load(f)
                    return self._config_cache
            except Exception as e:
                logger.error(f"Error loading suggestions config from {self.config_path}: {e}")

        # Default fallback config if file missing
        self._config_cache = {
            "welcome_message": "Hello 👋 I am the DDU AI Assistant. How can I help you today?",
            "primary_categories": [
                {"id": "admissions", "name": "Admissions & Cutoffs", "icon": "🎓", "description": "Eligibility, ACPC cutoffs"},
                {"id": "attendance", "name": "Attendance Rules", "icon": "📅", "description": "75% rule & condonation"},
                {"id": "placements", "name": "Placements & Internships", "icon": "💼", "description": "Recruiters & packages"},
                {"id": "examinations", "name": "Examinations & Grading", "icon": "📝", "description": "SPI/CPI & backlogs"},
                {"id": "fees_scholarships", "name": "Fees & Scholarships", "icon": "💰", "description": "Fees & MYSY details"},
            ],
            "sub_topics": {},
            "follow_up_map": {}
        }
        return self._config_cache

    def get_welcome_suggestions(self) -> SuggestionsResponse:
        """Returns structured welcome options and all subtopics."""
        config = self._load_config()
        primary_cats = [
            PrimaryCategory(
                id=c["id"],
                name=c["name"],
                icon=c.get("icon", "📌"),
                description=c.get("description", "")
            )
            for c in config.get("primary_categories", [])
        ]

        sub_topics_map = {}
        for cat_id, topics in config.get("sub_topics", {}).items():
            sub_topics_map[cat_id] = [
                SubTopic(label=t["label"], query=t["query"]) for t in topics
            ]

        return SuggestionsResponse(
            welcome_message=config.get("welcome_message", "Hello! How can I assist you with DDU information?"),
            primary_categories=primary_cats,
            sub_topics=sub_topics_map,
        )

    def get_subtopics_for_category(self, category_id: str) -> List[SubTopic]:
        """Returns subtopics for a specific category."""
        config = self._load_config()
        topics = config.get("sub_topics", {}).get(category_id, [])
        return [SubTopic(label=t["label"], query=t["query"]) for t in topics]

    def get_dynamic_follow_ups(self, category: str, query: str = "") -> List[str]:
        """Generates dynamic follow-up suggestions based on category and query context."""
        config = self._load_config()
        follow_ups_map = config.get("follow_up_map", {})

        # Primary category suggestions
        suggestions = follow_ups_map.get(category, [])
        if not suggestions:
            suggestions = follow_ups_map.get("general", [
                "Minimum Attendance Requirement",
                "Placement Statistics & Recruiters",
                "SPI and CPI Calculation Formula",
                "MYSY Scholarship Eligibility"
            ])

        # Filter out questions that are too similar to the original query
        query_lower = query.lower()
        filtered = [s for s in suggestions if not all(word in query_lower for word in s.lower().split()[:2])]

        return filtered[:4] if filtered else suggestions[:4]
