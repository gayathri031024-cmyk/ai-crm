"""
Structured argument schemas for every tool the CRM agent can call.
These double as the JSON-schema sent to Groq for tool-calling and as
runtime validation when the agent's tool call is executed.
"""
from pydantic import BaseModel, Field, field_validator


def _coerce_to_list(value):
    """
    Some models occasionally return a single string (e.g. "GlucoBalance")
    instead of a list (["GlucoBalance"]) for list-typed fields, especially
    smaller/faster models. Accept either shape instead of hard-failing.
    """
    if value is None:
        return value
    if isinstance(value, str):
        return [value]
    return value


class LogInteractionArgs(BaseModel):
    hcp_name: str = Field(description="Name of the healthcare professional, e.g. 'Dr. Sharma'")
    interaction_type: str = Field(
        default="visit",
        description="One of: visit, call, email, virtual_meeting, event",
    )
    visit_date: str = Field(
        description="ISO date or datetime of the interaction, e.g. '2026-07-13'. "
        "Use today's date if the user says 'today'."
    )
    discussion_summary: str | None = Field(default=None, description="What was discussed")
    products_discussed: list[str] | str | None = Field(
        default=None, description="Products/drugs mentioned. Provide as a list of strings."
    )
    samples_given: int = Field(default=0, description="Number of samples given, if any")
    sentiment: str | None = Field(default=None, description="One of: positive, neutral, negative")
    follow_up_date: str | None = Field(default=None, description="ISO date for the next follow-up, if mentioned")
    next_action: str | None = Field(default=None, description="Planned next action")
    notes: str | None = Field(default=None, description="Any other free-form notes")

    @field_validator("products_discussed", mode="before")
    @classmethod
    def _coerce_products_discussed(cls, v):
        return _coerce_to_list(v)


class EditInteractionArgs(BaseModel):
    hcp_name: str | None = Field(
        default=None,
        description="Name of the HCP whose most recent interaction should be edited, "
        "if the user doesn't reference a specific interaction directly",
    )
    interaction_id: str | None = Field(
        default=None, description="Exact interaction ID, if known"
    )
    samples_given: int | None = None
    discussion_summary: str | None = None
    products_discussed: list[str] | str | None = Field(
    default=None, description="Products/drugs mentioned. Provide as a list of strings."
    )
    sentiment: str | None = None
    follow_up_date: str | None = None
    next_action: str | None = None
    notes: str | None = None

    @field_validator("products_discussed", mode="before")
    @classmethod
    def _coerce_products_discussed(cls, v):
        return _coerce_to_list(v)


class SearchHCPArgs(BaseModel):
    query: str = Field(description="Name, hospital, city, or specialization to search for")


class ScheduleFollowUpArgs(BaseModel):
    hcp_name: str | None = Field(
        default=None, description="HCP whose latest interaction should get a follow-up date"
    )
    interaction_id: str | None = Field(default=None, description="Exact interaction ID, if known")
    follow_up_date: str = Field(description="ISO date for the follow-up, e.g. '2026-07-20'")


class GenerateVisitSummaryArgs(BaseModel):
    hcp_name: str | None = Field(default=None, description="HCP to summarize recent visits for")
    interaction_id: str | None = Field(default=None, description="Exact interaction ID, if known")
    limit: int = Field(default=5, description="Max number of recent interactions to include")