from .chat import router as chat_router
from .suggestions import router as suggestions_router
from .admin import router as admin_router
from .analytics import router as analytics_router

__all__ = ["chat_router", "suggestions_router", "admin_router", "analytics_router"]
