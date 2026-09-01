from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class DocumentChunkResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    document_id: str
    chunk_index: int
    content: str
    metadata_json: Dict[str, Any]


class DocumentCreate(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    file_type: str = Field(default="txt")
    content: Optional[str] = None
    url: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    file_type: str
    file_path: Optional[str] = None
    file_size: int
    content_summary: Optional[str] = None
    metadata_json: Dict[str, Any]
    chunks_count: Optional[int] = 0
    created_at: datetime
    updated_at: datetime


class SearchQuery(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)
    category: Optional[str] = None


class SearchResultItem(BaseModel):
    id: str
    type: str
    title: str
    snippet: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultItem]
    total: int
