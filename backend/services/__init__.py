__all__ = [
    "get_llm",
    "QueryClassifierService",
    "SuggestionService",
    "DocumentService",
    "RAGService",
]


def __getattr__(name):
    if name == "get_llm":
        from .llm_factory import get_llm

        return get_llm
    if name == "QueryClassifierService":
        from .classifier_service import QueryClassifierService

        return QueryClassifierService
    if name == "SuggestionService":
        from .suggestion_service import SuggestionService

        return SuggestionService
    if name == "DocumentService":
        from .document_service import DocumentService

        return DocumentService
    if name == "RAGService":
        from .rag_service import RAGService

        return RAGService
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
