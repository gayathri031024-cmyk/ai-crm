from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.hcp import HCP, HCPTier
from app.schemas.hcp import HCPCreate, HCPUpdate


class HCPRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: HCPCreate, created_by: str | None) -> HCP:
        hcp = HCP(**data.model_dump(), created_by=created_by)
        self.db.add(hcp)
        self.db.commit()
        self.db.refresh(hcp)
        return hcp

    def get(self, hcp_id: str) -> HCP | None:
        return self.db.get(HCP, hcp_id)

    def update(self, hcp: HCP, data: HCPUpdate) -> HCP:
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(hcp, field, value)
        self.db.commit()
        self.db.refresh(hcp)
        return hcp

    def delete(self, hcp: HCP) -> None:
        self.db.delete(hcp)
        self.db.commit()

    def list(
        self,
        page: int = 1,
        page_size: int = 20,
        search: str | None = None,
        tier: HCPTier | None = None,
        city: str | None = None,
        sort_by: str = "created_at",
        sort_dir: str = "desc",
    ) -> tuple[list[HCP], int]:
        query = self.db.query(HCP)

        if search:
            like = f"%{search}%"
            query = query.filter(
                or_(
                    HCP.full_name.ilike(like),
                    HCP.hospital_name.ilike(like),
                    HCP.city.ilike(like),
                    HCP.specialization.ilike(like),
                )
            )
        if tier:
            query = query.filter(HCP.tier == tier)
        if city:
            query = query.filter(HCP.city.ilike(f"%{city}%"))

        total = query.count()

        sort_column = getattr(HCP, sort_by, HCP.created_at)
        query = query.order_by(sort_column.desc() if sort_dir == "desc" else sort_column.asc())

        items = query.offset((page - 1) * page_size).limit(page_size).all()
        return items, total
