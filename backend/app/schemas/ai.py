from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ToolCallItem(BaseModel):
    id: str
    name: str
    arguments: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    status: str = "success"


class AIChatRequest(BaseModel):
    """Unified request schema for both text and voice chat."""
    conversation_id: Optional[str] = None
    message: str = Field(min_length=1)
    provider: Optional[str] = None
    model: Optional[str] = None
    temperature: Optional[float] = 0.7
    input_type: str = Field(default="text", description="'text' or 'voice'")


# Keep backward-compatible alias
AIChatMessageRequest = AIChatRequest


class AIChatResponse(BaseModel):
    conversation_id: str
    message_id: str
    reply: str
    role: str = "assistant"
    provider: str
    model: str
    tool_calls: Optional[List[ToolCallItem]] = None
    suggested_actions: Optional[List[Dict[str, Any]]] = None
    tokens_used: int = 0


class AIConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    title: str
    pinned: bool
    summary: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class AIMessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    conversation_id: str
    role: str
    content: str
    tool_calls: Optional[Any] = None
    tool_results: Optional[Any] = None
    model: Optional[str] = None
    created_at: datetime


class AIMemoryCreate(BaseModel):
    category: str = Field(default="fact")
    key: Optional[str] = None
    content: str = Field(min_length=1)
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    source: str = Field(default="explicit")


class AIMemoryUpdate(BaseModel):
    category: Optional[str] = None
    key: Optional[str] = None
    content: Optional[str] = None
    confidence: Optional[float] = None
    is_active: Optional[bool] = None


class AIMemoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    category: str
    key: Optional[str] = None
    content: str
    confidence: float
    is_active: bool
    source: str
    last_accessed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class ToolExecutionConfirmationRequest(BaseModel):
    confirmation_token: str
    approved: bool
