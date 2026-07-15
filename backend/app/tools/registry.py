"""
Central registry the agent graph uses to (a) advertise tool schemas to
Groq and (b) dispatch an incoming tool_call by name to the right function,
bound to the current DB session and user.
"""
from dataclasses import dataclass
from typing import Any, Callable

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.tools import crm_tools
from app.tools.schemas import (
    EditInteractionArgs,
    GenerateVisitSummaryArgs,
    LogInteractionArgs,
    ScheduleFollowUpArgs,
    SearchHCPArgs,
)


@dataclass
class ToolSpec:
    name: str
    description: str
    args_schema: type[BaseModel]
    # fn signature is always (db, user_id, args) even if user_id/db are unused,
    # for a uniform dispatch call site.
    fn: Callable[..., dict]
    needs_user: bool = True


TOOL_SPECS: list[ToolSpec] = [
    ToolSpec(
        name="log_interaction",
        description=(
            "Create a new structured HCP interaction record from natural language, e.g. "
            "'I met Dr. Sharma today, discussed insulin, gave 5 samples, follow up next Friday.'"
        ),
        args_schema=LogInteractionArgs,
        fn=lambda db, user_id, args: crm_tools.log_interaction(db, user_id, args),
    ),
    ToolSpec(
        name="edit_interaction",
        description=(
            "Edit an existing interaction the user already logged, e.g. "
            "'Actually it was 10 samples.' Defaults to the most recent interaction "
            "for the mentioned HCP (or the user's most recent interaction overall)."
        ),
        args_schema=EditInteractionArgs,
        fn=lambda db, user_id, args: crm_tools.edit_interaction(db, user_id, args),
    ),
    ToolSpec(
        name="search_hcp",
        description="Search for healthcare professionals by name, hospital, city, or specialization.",
        args_schema=SearchHCPArgs,
        fn=lambda db, user_id, args: crm_tools.search_hcp(db, args),
        needs_user=False,
    ),
    ToolSpec(
        name="schedule_follow_up",
        description="Set or move the follow-up date on an existing interaction.",
        args_schema=ScheduleFollowUpArgs,
        fn=lambda db, user_id, args: crm_tools.schedule_follow_up(db, user_id, args),
    ),
    ToolSpec(
        name="generate_visit_summary",
        description="Generate a readable recap of recent interactions for an HCP.",
        args_schema=GenerateVisitSummaryArgs,
        fn=lambda db, user_id, args: crm_tools.generate_visit_summary(db, args),
        needs_user=False,
    ),
]

TOOL_SPECS_BY_NAME: dict[str, ToolSpec] = {spec.name: spec for spec in TOOL_SPECS}


def build_groq_tool_definitions() -> list[dict[str, Any]]:
    """Builds the OpenAI/Groq-compatible `tools` array from our Pydantic schemas."""
    definitions = []
    for spec in TOOL_SPECS:
        schema = spec.args_schema.model_json_schema()
        # Groq/OpenAI tool schemas don't want pydantic's $defs/title noise
        schema.pop("title", None)
        definitions.append(
            {
                "type": "function",
                "function": {
                    "name": spec.name,
                    "description": spec.description,
                    "parameters": schema,
                },
            }
        )
    return definitions


def dispatch_tool_call(db: Session, user_id: str, tool_name: str, raw_args: dict) -> dict:
    """Validates raw_args against the tool's schema, then executes it."""
    spec = TOOL_SPECS_BY_NAME.get(tool_name)
    if spec is None:
        return {
            "status": "error",
            "message": f"Unknown tool '{tool_name}'.",
            "data": None,
        }
    try:
        parsed_args = spec.args_schema(**raw_args)
    except Exception as exc:  # pydantic ValidationError, bad JSON, etc.
        return {
            "status": "error",
            "message": f"Invalid arguments for '{tool_name}': {exc}",
            "data": None,
        }

    return spec.fn(db, user_id, parsed_args)
