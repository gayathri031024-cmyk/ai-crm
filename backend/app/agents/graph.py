"""
The CRM assistant's reasoning loop, built as a LangGraph StateGraph:

    START -> agent -> (tool calls?) -> tools -> agent -> ... -> END

`agent` calls Groq (with automatic primary/backup fallback) with the full
message history and the 5 tool schemas. If the model responds with tool
calls, we route to `tools`, execute them against the real DB, append the
results as tool messages, and loop back to `agent` so it can react to
what happened (e.g. confirm the save, or ask a clarifying question).
A hard iteration cap prevents infinite tool-calling loops.
"""
import json
import logging
from datetime import datetime

from langgraph.graph import END, StateGraph

from app.agents.groq_client import GroqClient
from app.agents.state import AgentState
from app.tools.registry import build_groq_tool_definitions, dispatch_tool_call

logger = logging.getLogger("ai_crm.agent")

MAX_TOOL_ITERATIONS = 4

SYSTEM_PROMPT = """You are an intelligent CRM assistant helping a pharmaceutical sales \
representative log and manage their interactions with healthcare professionals (HCPs).

Today's date is {today}.

You have exactly five tools. Use them whenever the user's intent matches, even if they \
don't ask for a tool by name:
- log_interaction: the user describes a NEW visit/call/interaction, e.g. "I met Dr. Sharma \
today, discussed insulin, gave 5 samples."
- edit_interaction: the user corrects or amends something already logged, e.g. "Actually \
it was 10 samples" or "change the sentiment to positive."
- search_hcp: the user wants to find/look up HCPs, e.g. "Find HCPs named Smith" or "who do \
we have in Mumbai?"
- schedule_follow_up: the user wants to set or move a follow-up date on an existing \
interaction, e.g. "Move the follow-up for Dr. Smith to next Friday."
- generate_visit_summary: the user wants a recap of past visits, e.g. "Summarize my recent \
visits with Dr. Smith" or "what's the history with this HCP?"

Rules:
- Resolve relative dates yourself ("today", "next Friday", "tomorrow") into ISO dates \
(YYYY-MM-DD) before calling any tool — don't pass the phrase through unresolved.
- If a tool tells you it needs clarification (e.g. ambiguous or unknown HCP name), ask the \
user directly instead of guessing.
- After a tool succeeds, confirm what you did in one short, friendly sentence. Don't repeat \
back the raw tool output verbatim.
- Only call one tool at a time, and only when you have enough information to do so \
confidently.
- Do not call the same tool with the same arguments more than once in a single turn.
"""


def _build_system_message() -> dict:
    return {
        "role": "system",
        "content": SYSTEM_PROMPT.format(today=datetime.utcnow().date().isoformat()),
    }


def _agent_node(state: AgentState, config: dict) -> dict:
    db = config["configurable"]["db"]
    user_id = config["configurable"]["user_id"]
    groq_client: GroqClient = config["configurable"]["groq_client"]

    messages = state["messages"]
    if not messages or messages[0].get("role") != "system":
        messages = [_build_system_message()] + messages

    tool_defs = build_groq_tool_definitions()
    message, model_used = groq_client.chat_completion(messages=messages, tools=tool_defs)

    assistant_msg = {
        "role": "assistant",
        "content": message.content or "",
        "model_used": model_used,
    }
    if getattr(message, "tool_calls", None):
        assistant_msg["tool_calls"] = [
            {
                "id": tc.id,
                "type": "function",
                "function": {"name": tc.function.name, "arguments": tc.function.arguments},
            }
            for tc in message.tool_calls
        ]

    return {"messages": [assistant_msg], "iterations": state.get("iterations", 0) + 1}


def _tools_node(state: AgentState, config: dict) -> dict:
    db = config["configurable"]["db"]
    user_id = config["configurable"]["user_id"]

    last_message = state["messages"][-1]
    tool_messages = []

    for tool_call in last_message.get("tool_calls", []):
        name = tool_call["function"]["name"]
        try:
            args = json.loads(tool_call["function"]["arguments"])
        except json.JSONDecodeError:
            args = {}

        result = dispatch_tool_call(db, user_id, name, args)
        logger.info("tool=%s status=%s", name, result.get("status"))

        tool_messages.append(
            {
                "role": "tool",
                "tool_call_id": tool_call["id"],
                "name": name,
                "content": json.dumps(result),
            }
        )

    return {"messages": tool_messages}


def _route_after_agent(state: AgentState) -> str:
    last_message = state["messages"][-1]
    if last_message.get("tool_calls") and state.get("iterations", 0) < MAX_TOOL_ITERATIONS:
        return "tools"
    return END


def build_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", _agent_node)
    graph.add_node("tools", _tools_node)
    graph.set_entry_point("agent")
    graph.add_conditional_edges("agent", _route_after_agent, {"tools": "tools", END: END})
    graph.add_edge("tools", "agent")
    return graph.compile()


# Compiled once at import time — the graph structure itself is stateless;
# per-request data (db, user_id, groq_client) flows through `config`.
crm_agent_graph = build_agent_graph()
