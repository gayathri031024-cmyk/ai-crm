from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.agents.groq_client import GroqClient
from app.core.dependencies import get_current_user, get_groq_client
from app.database.session import get_db
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse, ConversationDetailOut, ConversationOut
from app.services.chat_service import ChatService

router = APIRouter(tags=["chat"])


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    groq_client: GroqClient = Depends(get_groq_client),
):
    service = ChatService(db, user_id=current_user.id, groq_client=groq_client)
    conv, saved_rows = service.send_message(payload.message, payload.conversation_id)

    # The reply shown to the user is the last assistant message with no pending tool calls
    assistant_replies = [r for r in saved_rows if r.role.value == "assistant"]
    reply_text = assistant_replies[-1].content if assistant_replies else ""

    return ChatResponse(conversation_id=conv.id, reply=reply_text, messages=saved_rows)


@router.get("/history", response_model=list[ConversationOut])
def history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db, user_id=current_user.id, groq_client=None)  # not needed for read-only listing
    return service.list_conversations()


@router.get("/history/{conversation_id}", response_model=ConversationDetailOut)
def conversation_detail(
    conversation_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = ChatService(db, user_id=current_user.id, groq_client=None)
    conv = service.get_conversation_or_404(conversation_id)
    return ConversationDetailOut(
        id=conv.id,
        title=conv.title,
        started_at=conv.started_at,
        ended_at=conv.ended_at,
        messages=conv.messages,
    )
