from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.core.dependencies import get_current_user
from app.database.session import get_db
from app.models.hcp import HCPTier
from app.models.user import User
from app.schemas.common import build_pagination_meta
from app.schemas.hcp import HCPCreate, HCPOut, HCPUpdate, PaginatedHCPs
from app.services.hcp_service import HCPService

router = APIRouter(prefix="/hcps", tags=["hcps"])


@router.post("", response_model=HCPOut, status_code=status.HTTP_201_CREATED)
def create_hcp(
    payload: HCPCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = HCPService(db)
    return service.create_hcp(payload, created_by=current_user.id)


@router.get("", response_model=PaginatedHCPs)
def list_hcps(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    search: str | None = Query(default=None, description="Search name, hospital, city, specialization"),
    tier: HCPTier | None = None,
    city: str | None = None,
    sort_by: str = Query(default="created_at"),
    sort_dir: str = Query(default="desc", pattern="^(asc|desc)$"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    service = HCPService(db)
    items, total = service.list_hcps(page, page_size, search, tier, city, sort_by, sort_dir)
    return PaginatedHCPs(items=items, meta=build_pagination_meta(total, page, page_size))


@router.get("/{hcp_id}", response_model=HCPOut)
def get_hcp(
    hcp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HCPService(db).get_hcp_or_404(hcp_id)


@router.put("/{hcp_id}", response_model=HCPOut)
def update_hcp(
    hcp_id: str,
    payload: HCPUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return HCPService(db).update_hcp(hcp_id, payload)


@router.delete("/{hcp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_hcp(
    hcp_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    HCPService(db).delete_hcp(hcp_id)
