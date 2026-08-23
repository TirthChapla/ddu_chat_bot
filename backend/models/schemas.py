"""
Pydantic Schemas for DDU AI Assistant
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="'user' or 'assistant'")
    content: str = Field(..., description="Message text content")


class ChatRequest(BaseModel):
    query: str = Field(..., description="User query text")
    category: Optional[str] = Field(None, description="Optional category filter (e.g. 'attendance', 'placements')")
    history: Optional[List[ChatMessage]] = Field(default=[], description="Previous conversation messages")


class SourceCitation(BaseModel):
    doc_id: str
    source: str
    category: str
    page: Optional[int] = 1
    snippet: str
    similarity_score: float


class ChatResponse(BaseModel):
    query: str
    answer: str
    category: str
    sources: List[SourceCitation]
    follow_up_suggestions: List[str]
    latency_ms: float
    confidence: str


class PrimaryCategory(BaseModel):
    id: str
    name: str
    icon: str
    description: str


class SubTopic(BaseModel):
    label: str
    query: str


class SuggestionsResponse(BaseModel):
    welcome_message: str
    primary_categories: List[PrimaryCategory]
    sub_topics: Dict[str, List[SubTopic]]


class DocumentInfo(BaseModel):
    doc_id: str
    source: str
    category: str
    file_type: str
    chunk_count: int


class AdminStatsResponse(BaseModel):
    total_chunks: int
    total_documents: int
    categories: Dict[str, int]
    documents: List[DocumentInfo]


class UploadResponse(BaseModel):
    success: bool
    doc_id: Optional[str] = None
    filename: str
    category: Optional[str] = None
    chunks_added: int = 0
    message: str = ""


class QueryLog(BaseModel):
    timestamp: str
    query: str
    category: str
    latency_ms: float
    sources_count: int
