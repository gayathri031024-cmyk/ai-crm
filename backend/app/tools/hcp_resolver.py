from sqlalchemy.orm import Session

from app.models.hcp import HCP
from app.repositories.hcp_repository import HCPRepository


class HCPResolution:
    """Result of trying to resolve a free-text HCP name to a single record."""

    def __init__(self, hcp: HCP | None = None, candidates: list[HCP] | None = None):
        self.hcp = hcp
        self.candidates = candidates or []

    @property
    def is_resolved(self) -> bool:
        return self.hcp is not None

    @property
    def needs_clarification(self) -> bool:
        return self.hcp is None and len(self.candidates) > 0

    @property
    def not_found(self) -> bool:
        return self.hcp is None and len(self.candidates) == 0


def resolve_hcp_by_name(db: Session, name: str) -> HCPResolution:
    repo = HCPRepository(db)
    matches, _total = repo.list(page=1, page_size=5, search=name)

    if len(matches) == 1:
        return HCPResolution(hcp=matches[0])

    # Exact case-insensitive name match disambiguates even if search returned several
    exact = [m for m in matches if m.full_name.strip().lower() == name.strip().lower()]
    if len(exact) == 1:
        return HCPResolution(hcp=exact[0])

    if len(matches) == 0:
        return HCPResolution(candidates=[])

    return HCPResolution(candidates=matches)
