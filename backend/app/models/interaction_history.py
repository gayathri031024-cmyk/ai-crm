import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.session import Base


class ChangeSource(str, PyEnum):
    form = "form"
    ai_chat = "ai_chat"


class InteractionHistory(Base):
    __tablename__ = "interaction_history"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    interaction_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("interactions.id", ondelete="CASCADE"), nullable=False
    )
    changed_by: Mapped[str] = mapped_column(
        String(36), ForeignKey("users.id", ondelete="RESTRICT"), nullable=False
    )
    change_source: Mapped[ChangeSource] = mapped_column(
        Enum(ChangeSource), default=ChangeSource.form, nullable=False
    )
    field_name: Mapped[str] = mapped_column(String(100), nullable=False)
    old_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_value: Mapped[str | None] = mapped_column(Text, nullable=True)
    changed_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    interaction: Mapped["Interaction"] = relationship("Interaction", back_populates="history")
