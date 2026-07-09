from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.domain.models.campaign import CampaignStatus, DeviceType


class CampaignTargetCreate(BaseModel):
    country: str = Field(min_length=2, max_length=8)
    device_type: DeviceType
    placement_id: int


class CampaignTargetRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    country: str
    device_type: DeviceType
    placement_id: int


class CampaignCreate(BaseModel):
    name: str
    advertiser_name: str
    status: CampaignStatus = CampaignStatus.draft
    bid_cpm: Decimal = Field(gt=0)
    daily_budget: Decimal = Field(gt=0)
    remaining_budget: Decimal = Field(ge=0)
    frequency_cap: int = Field(ge=1)
    targets: list[CampaignTargetCreate] = Field(min_length=1)


class CampaignUpdate(BaseModel):
    name: str | None = None
    advertiser_name: str | None = None
    status: CampaignStatus | None = None
    bid_cpm: Decimal | None = Field(default=None, gt=0)
    daily_budget: Decimal | None = Field(default=None, gt=0)
    remaining_budget: Decimal | None = Field(default=None, ge=0)
    frequency_cap: int | None = Field(default=None, ge=1)
    targets: list[CampaignTargetCreate] | None = Field(default=None, min_length=1)


class CampaignRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    advertiser_name: str
    status: CampaignStatus
    bid_cpm: Decimal
    daily_budget: Decimal
    remaining_budget: Decimal
    frequency_cap: int
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime
    targets: list[CampaignTargetRead]
