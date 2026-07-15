from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.hcp import HCP, HCPTier
from app.repositories.hcp_repository import HCPRepository
from app.schemas.hcp import HCPCreate, HCPUpdate


class HCPService:
    def __init__(self, db: Session):
        self.repo = HCPRepository(db)

    def create_hcp(self, data: HCPCreate, created_by: str) -> HCP:
        return self.repo.create(data, created_by)

    def get_hcp_or_404(self, hcp_id: str) -> HCP:
        hcp = self.repo.get(hcp_id)
        if not hcp:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="HCP not found")
        return hcp

    def update_hcp(self, hcp_id: str, data: HCPUpdate) -> HCP:
        hcp = self.get_hcp_or_404(hcp_id)
        return self.repo.update(hcp, data)

    def delete_hcp(self, hcp_id: str) -> None:
        hcp = self.get_hcp_or_404(hcp_id)
        self.repo.delete(hcp)

    def list_hcps(
        self,
        page: int,
        page_size: int,
        search: str | None,
        tier: HCPTier | None,
        city: str | None,
        sort_by: str,
        sort_dir: str,
    ):
        return self.repo.list(
            page=page,
            page_size=page_size,
            search=search,
            tier=tier,
            city=city,
            sort_by=sort_by,
            sort_dir=sort_dir,
        )
