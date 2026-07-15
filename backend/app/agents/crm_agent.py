from sqlalchemy.orm import Session

from app.agents.graph import crm_agent_graph
from app.agents.groq_client import GroqClient


def run_agent_turn(
    db: Session,
    user_id: str,
    conversation_history: list[dict],
    user_message: str,
    groq_client: GroqClient | None = None,
) -> list[dict]:
    """
    Runs one turn of the CRM assistant.

    `conversation_history` is the prior turns in plain dict form (as stored
    in ai_messages), NOT including the new user_message.

    Returns the list of *new* messages produced this turn (the user message,
    any assistant/tool messages from tool-calling round-trips, and the final
    assistant reply) — the caller persists these to ai_messages.
    """
    client = groq_client or GroqClient()

    initial_messages = conversation_history + [{"role": "user", "content": user_message}]
    initial_state = {"messages": initial_messages, "iterations": 0}

    config = {"configurable": {"db": db, "user_id": user_id, "groq_client": client}}
    final_state = crm_agent_graph.invoke(initial_state, config=config)

    # Only the messages generated *this turn* (history + new ones minus history)
    new_messages = final_state["messages"][len(conversation_history):]
    return new_messages
