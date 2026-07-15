import uuid
from datetime import date, datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Date, Enum, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class InteractionType(str, PyEnum):
    visit = "visit"
    call = "call"
    email = "email"
    virtual_meeting = "virtual_meeting"
    event = "event"


class Sentiment(str, PyEnum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class CreatedVia(str, PyEnum):
    form = "form"
    ai_chat = "ai_chat"


class Interaction(Base):
    __tablename__ = "interactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    hcp_id: Mapped[str] = mapped_column(String(36), ForeignKey("hcps.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    interaction_type: Mapped[InteractionType] = mapped_column(
        Enum(InteractionType), default=InteractionType.visit, nullable=False
    )
    visit_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    follow_up_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    discussion_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    products_discussed: Mapped[list | None] = mapped_column(JSON, nullable=True)
    samples_given: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    sentiment: Mapped[Sentiment | None] = mapped_column(Enum(Sentiment), nullable=True)
    next_action: Mapped[str | None] = mapped_column(String(255), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_via: Mapped[CreatedVia] = mapped_column(Enum(CreatedVia), default=CreatedVia.form, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )

    hcp: Mapped["HCP"] = relationship("HCP", back_populates="interactions")
    user: Mapped["User"] = relationship("User", back_populates="interactions")
    history: Mapped[list["InteractionHistory"]] = relationship(
        "InteractionHistory", back_populates="interaction", cascade="all, delete-orphan"
    )
