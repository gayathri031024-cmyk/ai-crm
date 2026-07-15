from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.hcp import HCPTier
from app.schemas.common import PaginationMeta


class HCPBase(BaseModel):
    full_name: str = Field(min_length=2, max_length=150)
    specialization: str | None = Field(default=None, max_length=150)
    hospital_name: str | None = Field(default=None, max_length=200)
    phone: str | None = Field(default=None, max_length=30)
    email: EmailStr | None = None
    city: str | None = Field(default=None, max_length=120)
    tier: HCPTier = HCPTier.B
    notes: str | None = None


class HCPCreate(HCPBase):
    pass


class HCPUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=150)
    specialization: str | None = None
    hospital_name: str | None = None
    phone: str | None = None
    email: EmailStr | None = None
    city: str | None = None
    tier: HCPTier | None = None
    notes: str | None = None


class HCPOut(HCPBase):
    model_config = ConfigDict(from_attributes=True)

    id: str
    created_at: datetime
    updated_at: datetime


class PaginatedHCPs(BaseModel):
    items: list[HCPOut]
    meta: PaginationMeta