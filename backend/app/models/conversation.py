from datetime import datetime

from pydantic import BaseModel, Field

from app.models.chat import ChatMessage, UsageStats


class ConversationSummary(BaseModel):
    id: str
    title: str
    updated_at: datetime


class ConversationDetail(BaseModel):
    id: str
    title: str
    created_at: datetime
    updated_at: datetime
    messages: list[ChatMessage]


class CreateConversationRequest(BaseModel):
    title: str = Field(default="New Chat", max_length=200)


class CreateConversationResponse(BaseModel):
    id: str
    title: str
    created_at: datetime


class StoredMessage(BaseModel):
    role: str
    content: str
    usage: UsageStats | None = None
