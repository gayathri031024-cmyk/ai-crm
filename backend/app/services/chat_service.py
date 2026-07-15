import json

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agents.crm_agent import run_agent_turn
from app.agents.groq_client import GroqClient
from app.models.conversation import AIMessage, ConversationLog, MessageRole


class ChatService:
    def __init__(self, db: Session, user_id: str, groq_client: GroqClient):
        self.db = db
        self.user_id = user_id
        self.groq_client = groq_client

    # -----------------------------------------------------------------
    # Conversation lifecycle
    # -----------------------------------------------------------------
    def get_or_create_conversation(self, conversation_id: str | None) -> ConversationLog:
        if conversation_id:
            conv = self.db.get(ConversationLog, conversation_id)
            if not conv:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
            if conv.user_id != self.user_id:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your conversation")
            return conv

        conv = ConversationLog(user_id=self.user_id)
        self.db.add(conv)
        self.db.commit()
        self.db.refresh(conv)
        return conv

    def list_conversations(self) -> list[ConversationLog]:
        return (
            self.db.query(ConversationLog)
            .filter(ConversationLog.user_id == self.user_id)
            .order_by(ConversationLog.started_at.desc())
            .all()
        )

    def get_conversation_or_404(self, conversation_id: str) -> ConversationLog:
        conv = self.db.get(ConversationLog, conversation_id)
        if not conv or conv.user_id != self.user_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversation not found")
        return conv

    # -----------------------------------------------------------------
    # Message <-> DB row conversion
    # -----------------------------------------------------------------
    @staticmethod
    def _db_row_to_agent_dict(row: AIMessage) -> dict:
        """Reconstructs the plain dict format run_agent_turn/Groq expects from a stored row."""
        if row.role == MessageRole.tool:
            return {
                "role": "tool",
                "tool_call_id": (row.tool_input or {}).get("tool_call_id"),
                "name": row.tool_name,
                "content": json.dumps(row.tool_output) if row.tool_output is not None else (row.content or ""),
            }
        msg = {"role": row.role.value, "content": row.content or ""}
        if row.role == MessageRole.assistant and row.tool_input and "tool_calls" in row.tool_input:
            msg["tool_calls"] = row.tool_input["tool_calls"]
        return msg

    def _load_history(self, conversation_id: str) -> list[dict]:
        rows = (
            self.db.query(AIMessage)
            .filter(AIMessage.conversation_id == conversation_id)
            .order_by(AIMessage.created_at)
            .all()
        )
        return [self._db_row_to_agent_dict(r) for r in rows]

    def _persist_new_messages(self, conversation_id: str, new_messages: list[dict]) -> list[AIMessage]:
        saved: list[AIMessage] = []
        for msg in new_messages:
            role = msg["role"]
            if role == "tool":
                try:
                    tool_output = json.loads(msg["content"])
                except (json.JSONDecodeError, TypeError):
                    tool_output = None
                row = AIMessage(
                    conversation_id=conversation_id,
                    role=MessageRole.tool,
                    content=msg["content"],
                    tool_name=msg.get("name"),
                    tool_input={"tool_call_id": msg.get("tool_call_id")},
                    tool_output=tool_output,
                )
            elif role == "assistant":
                tool_input = {"tool_calls": msg["tool_calls"]} if msg.get("tool_calls") else None
                first_tool_name = msg["tool_calls"][0]["function"]["name"] if msg.get("tool_calls") else None
                row = AIMessage(
                    conversation_id=conversation_id,
                    role=MessageRole.assistant,
                    content=msg.get("content") or "",
                    tool_name=first_tool_name,
                    tool_input=tool_input,
                    model_used=msg.get("model_used"),
                )
            else:  # user
                row = AIMessage(
                    conversation_id=conversation_id,
                    role=MessageRole.user,
                    content=msg["content"],
                )
            self.db.add(row)
            saved.append(row)

        self.db.commit()
        for row in saved:
            self.db.refresh(row)
        return saved

    # -----------------------------------------------------------------
    # Main entrypoint
    # -----------------------------------------------------------------
    def send_message(self, message: str, conversation_id: str | None) -> tuple[ConversationLog, list[AIMessage]]:
        conv = self.get_or_create_conversation(conversation_id)
        history = self._load_history(conv.id)

        new_messages = run_agent_turn(
            db=self.db,
            user_id=self.user_id,
            conversation_history=history,
            user_message=message,
            groq_client=self.groq_client,
        )
        saved_rows = self._persist_new_messages(conv.id, new_messages)

        # Auto-title the conversation from the first user message
        if conv.title is None:
            conv.title = message[:80]
            self.db.commit()

        return conv, saved_rows
