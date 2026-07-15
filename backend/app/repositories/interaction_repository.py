from datetime import date, datetime

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.interaction import Interaction, InteractionType, Sentiment


class InteractionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, interaction: Interaction) -> Interaction:
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def get(self, interaction_id: str) -> Interaction | None:
        return self.db.get(Interaction, interaction_id)

    def delete(self, interaction: Interaction) -> None:
        self.db.delete(interaction)
        self.db.commit()

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        hcp_id: str | None = None,
        user_id: str | None = None,
        interaction_type: InteractionType | None = None,
        sentiment: Sentiment | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        search: str | None = None,
        sort_by: str = "visit_date",
        sort_dir: str = "desc",
    ) -> tuple[list[Interaction], int]:
        query = self.db.query(Interaction)

        if hcp_id:
            query = query.filter(Interaction.hcp_id == hcp_id)
        if user_id:
            query = query.filter(Interaction.user_id == user_id)
        if interaction_type:
            query = query.filter(Interaction.interaction_type == interaction_type)
        if sentiment:
            query = query.filter(Interaction.sentiment == sentiment)
        if date_from:
            query = query.filter(Interaction.visit_date >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(Interaction.visit_date <= datetime.combine(date_to, datetime.max.time()))
        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(Interaction.discussion_summary.ilike(like), Interaction.notes.ilike(like))
            )

        total = query.count()

        sort_column = getattr(Interaction, sort_by, Interaction.visit_date)
        query = query.order_by(sort_column.desc() if sort_dir == "desc" else sort_column.asc())

        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total

    def pending_follow_ups_count(self, user_id: str | None = None) -> int:
        today = datetime.utcnow().date()
        query = self.db.query(Interaction).filter(
            Interaction.follow_up_date.isnot(None), Interaction.follow_up_date >= today
        )
        if user_id:
            query = query.filter(Interaction.user_id == user_id)
        return query.count()

    def today_visits_count(self, user_id: str | None = None) -> int:
        today = datetime.utcnow().date()
        query = self.db.query(Interaction).filter(
            Interaction.visit_date >= datetime.combine(today, datetime.min.time()),
            Interaction.visit_date <= datetime.combine(today, datetime.max.time()),
        )
        if user_id:
            query = query.filter(Interaction.user_id == user_id)
        return query.count()
