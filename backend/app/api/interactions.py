from datetime import date

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.interaction import InteractionType, Sentiment
from app.models.interaction_history import ChangeSource
from app.models.user import User
from app.schemas.common import build_pagination_meta
from app.schemas.interaction import (
    InteractionCreate,
    InteractionHistoryOut,
    InteractionOut,
    InteractionUpdate,
    PaginatedInteractions,
)
from app.services.interaction_service import InteractionService

router = APIRouter(prefix="/interactions", tags=["interactions"])


@router.post("", response_model=InteractionOut, status_code=status.HTTP_201_CREATED)
def create_interaction(
    payload: InteractionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InteractionService(db).create_interaction(payload, user_id=current_user.id)


@router.get("", response_model=PaginatedInteractions)
def list_interactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    hcp_id: str | None = None,
    user_id: str | None = None,
    interaction_type: InteractionType | None = None,
    sentiment: Sentiment | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    search: str | None = Query(default=None, description="Search discussion summary and notes"),
    sort_by: str = Query(default="visit_date"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    items, total = service.list_interactions(
        page=page,
        page_size=page_size,
        hcp_id=hcp_id,
        user_id=user_id,
        interaction_type=interaction_type,
        sentiment=sentiment,
        date_from=date_from,
        date_to=date_to,
        search=search,
        sort_by=sort_by,
        sort_dir=sort_dir,
    )
    return PaginatedInteractions(items=items, meta=build_pagination_meta(total, page, page_size))


@router.get("/dashboard/summary")
def dashboard_summary(
    mine_only: bool = Query(default=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = InteractionService(db)
    return service.dashboard_counts(user_id=current_user.id if mine_only else None)


@router.get("/{interaction_id}", response_model=InteractionOut)
def get_interaction(
    interaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InteractionService(db).get_interaction_or_404(interaction_id)


@router.put("/{interaction_id}", response_model=InteractionOut)
def update_interaction(
    interaction_id: str,
    payload: InteractionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InteractionService(db).update_interaction(
        interaction_id, payload, changed_by=current_user.id, source=ChangeSource.form
    )


@router.delete("/{interaction_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interaction(
    interaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    InteractionService(db).delete_interaction(interaction_id)


@router.get("/{interaction_id}/history", response_model=list[InteractionHistoryOut])
def get_interaction_history(
    interaction_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return InteractionService(db).get_history(interaction_id)
