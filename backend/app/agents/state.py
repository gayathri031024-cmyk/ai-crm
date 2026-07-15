import operator
from typing import Annotated, TypedDict


class AgentState(TypedDict):
    """
    `messages` holds the full turn-by-turn conversation in plain
    OpenAI/Groq-compatible dict form: {"role": ..., "content": ..., ...}.
    Using operator.add as the reducer means every node that returns
    {"messages": [...]} appends rather than overwrites.
    """

    messages: Annotated[list[dict], operator.add]
    iterations: int
