__all__ = [
    "DocumentLoader",
    "infer_category_from_filename",
    "DocumentChunker",
    "ChromaIndexer",
    "get_embedding_function",
]


def __getattr__(name):
    if name in {"DocumentLoader", "infer_category_from_filename"}:
        from .loader import DocumentLoader, infer_category_from_filename

        return {"DocumentLoader": DocumentLoader, "infer_category_from_filename": infer_category_from_filename}[name]
    if name == "DocumentChunker":
        from .chunker import DocumentChunker

        return DocumentChunker
    if name in {"ChromaIndexer", "get_embedding_function"}:
        from .indexer import ChromaIndexer, get_embedding_function

        return {"ChromaIndexer": ChromaIndexer, "get_embedding_function": get_embedding_function}[name]
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
