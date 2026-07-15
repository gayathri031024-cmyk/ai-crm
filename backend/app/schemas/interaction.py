from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.interaction import CreatedVia, InteractionType, Sentiment
from app.schemas.common import PaginationMeta


class InteractionBase(BaseModel):
    hcp_id: str
    interaction_type: InteractionType = InteractionType.visit
    visit_date: datetime
    follow_up_date: date | None = None
    discussion_summary: str | None = None
    products_discussed: list[str] | None = None
    samples_given: int = Field(default=0, ge=0, le=100_000)
    sentiment: Sentiment | None = None
    next_action: str | None = Field(default=None, max_length=255)
    notes: str | None = None

    @field_validator("follow_up_date")
    @classmethod
    def follow_up_after_visit(cls, v: date | None, info):
        visit_date = info.data.get("visit_date")
        if v is not None and visit_date is not None and v < visit_date.date():
            raise ValueError("follow_up_date cannot be before visit_date")
        return v


class InteractionCreate(InteractionBase):
    created_via: CreatedVia = CreatedVia.form


class InteractionUpdate(BaseModel):
    """All fields optional — partial update (PUT semantics handled in service layer)."""
    interaction_type: InteractionType | None = None
    visit_date: datetime | None = None
    follow_up_date: date | None = None
    discussion_summary: str | None = None
    products_discussed: list[str] | None = None
    samples_given: int | None = Field(default=None, ge=0, le=100_000)
    sentiment: Sentiment | None = None
    next_action: str | None = None
    notes: str | None = None


class InteractionOut(InteractionBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    user_id: str
    created_via: CreatedVia
    created_at: datetime
    updated_at: datetime


class InteractionHistoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    interaction_id: str
    changed_by: str
    change_source: str
    field_name: str
    old_value: str | None
    new_value: str | None
    changed_at: datetime


class PaginatedInteractions(BaseModel):
    items: list[InteractionOut]
    meta: PaginationMeta