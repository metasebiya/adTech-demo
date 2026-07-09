from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from core.domain.models.auction import CandidateStatus, DecisionStatus
from core.domain.models.campaign import DeviceType


class BidRequestCreate(BaseModel):
    publisher_id: int
    placement_id: int
    country: str = Field(min_length=2, max_length=8)
    device_type: DeviceType
    user_id: str = Field(min_length=1, max_length=255)


class BidRequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publisher_id: int
    placement_id: int
    country: str
    device_type: DeviceType
    user_id: str
    created_at: datetime


class AuctionCandidateRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    campaign_id: int
    eligibility_status: CandidateStatus
    rejection_reason: str | None
    score: Decimal | None


class AuctionDecisionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    bid_request_id: int
    winner_campaign_id: int | None
    decision_status: DecisionStatus
    clearing_price: Decimal | None
    decision_reason: str
    created_at: datetime
    candidates: list[AuctionCandidateRead]


class BidRequestAuctionResponse(BaseModel):
    bid_request: BidRequestRead
    auction_decision: AuctionDecisionRead
