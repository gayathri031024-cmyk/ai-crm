from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None


class ChatMessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    role: str
    content: str
    tool_name: str | None = None
    tool_output: dict | None = None
    model_used: str | None = None
    created_at: datetime


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str
    messages: list[ChatMessageOut]  # full new turn, including any tool activity


class ConversationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str | None
    started_at: datetime
    ended_at: datetime | None


class ConversationDetailOut(BaseModel):
    id: str
    title: str | None
    started_at: datetime
    ended_at: datetime | None
    messages: list[ChatMessageOut]
