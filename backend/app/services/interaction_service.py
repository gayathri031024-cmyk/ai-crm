from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.interaction import CreatedVia, Interaction
from app.models.interaction_history import ChangeSource, InteractionHistory
from app.repositories.hcp_repository import HCPRepository
from app.repositories.interaction_repository import InteractionRepository
from app.schemas.interaction import InteractionCreate, InteractionUpdate

# Fields that, if changed, get written to interaction_history for audit purposes.
TRACKED_FIELDS = [
    "interaction_type",
    "visit_date",
    "follow_up_date",
    "discussion_summary",
    "products_discussed",
    "samples_given",
    "sentiment",
    "next_action",
    "notes",
]


class InteractionService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = InteractionRepository(db)
        self.hcp_repo = HCPRepository(db)

    def create_interaction(self, data: InteractionCreate, user_id: str) -> Interaction:
        hcp = self.hcp_repo.get(data.hcp_id)
        if not hcp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found")

        interaction = Interaction(
            hcp_id=data.hcp_id,
            user_id=user_id,
            interaction_type=data.interaction_type,
            visit_date=data.visit_date,
            follow_up_date=data.follow_up_date,
            discussion_summary=data.discussion_summary,
            products_discussed=data.products_discussed,
            samples_given=data.samples_given,
            sentiment=data.sentiment,
            next_action=data.next_action,
            notes=data.notes,
            created_via=data.created_via,
        )
        return self.repo.create(interaction)

    def get_interaction_or_404(self, interaction_id: str, requesting_user_id: str | None = None) -> Interaction:
        interaction = self.repo.get(interaction_id)
        if not interaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
        if requesting_user_id is not None and interaction.user_id != requesting_user_id:

            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interaction not found")
        return interaction
    
    def update_interaction(
        self,
        interaction_id: str,
        data: InteractionUpdate,
        changed_by: str,
        source: ChangeSource = ChangeSource.form,
    ) -> Interaction:
        """
        Applies a partial update and writes one InteractionHistory row per
        field that actually changed — this is what powers both the
        Interaction Timeline's edit trail and the "actually it was 10
        samples" AI edit-tool scenario.
        """
        interaction = self.get_interaction_or_404(interaction_id)
        updates = data.model_dump(exclude_unset=True)

        history_rows: list[InteractionHistory] = []
        for field, new_value in updates.items():
            if field not in TRACKED_FIELDS:
                continue
            old_value = getattr(interaction, field)
            if old_value == new_value:
                continue
            history_rows.append(
                InteractionHistory(
                    interaction_id=interaction.id,
                    changed_by=changed_by,
                    change_source=source,
                    field_name=field,
                    old_value=str(old_value) if old_value is not None else None,
                    new_value=str(new_value) if new_value is not None else None,
                )
            )
            setattr(interaction, field, new_value)

        if history_rows:
            self.db.add_all(history_rows)
        self.db.commit()
        self.db.refresh(interaction)
        return interaction

    def delete_interaction(self, interaction_id: str) -> None:
        interaction = self.get_interaction_or_404(interaction_id)
        self.repo.delete(interaction)

    def list_interactions(self, **filters):
        return self.repo.list(**filters)

    def get_history(self, interaction_id: str) -> list[InteractionHistory]:
        self.get_interaction_or_404(interaction_id)
        return (
            self.db.query(InteractionHistory)
            .filter(InteractionHistory.interaction_id == interaction_id)
            .order_by(InteractionHistory.changed_at.desc())
            .all()
        )

    def dashboard_counts(self, user_id: str | None = None) -> dict:
        return {
            "todays_visits": self.repo.today_visits_count(user_id),
            "pending_follow_ups": self.repo.pending_follow_ups_count(user_id),
        }
