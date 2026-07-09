from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.domain.models.base import Base
from core.domain.models.campaign import DeviceType


class DecisionStatus(str, Enum):
    win = "win"
    no_bid = "no_bid"


class CandidateStatus(str, Enum):
    eligible = "eligible"
    rejected = "rejected"


class RejectionReason(str, Enum):
    inactive = "inactive"
    country_mismatch = "country_mismatch"
    device_mismatch = "device_mismatch"
    placement_mismatch = "placement_mismatch"
    budget_exhausted = "budget_exhausted"
    frequency_cap_reached = "frequency_cap_reached"
    no_eligible_campaign = "no_eligible_campaign"


class BidRequest(Base):
    __tablename__ = "bid_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"), nullable=False, index=True)
    placement_id: Mapped[int] = mapped_column(ForeignKey("placements.id"), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(8), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(SqlEnum(DeviceType), nullable=False)
    user_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    auction_decision: Mapped["AuctionDecision | None"] = relationship(
        back_populates="bid_request",
        uselist=False,
        cascade="all, delete-orphan",
    )


class AuctionDecision(Base):
    __tablename__ = "auction_decisions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bid_request_id: Mapped[int] = mapped_column(ForeignKey("bid_requests.id"), nullable=False, index=True, unique=True)
    winner_campaign_id: Mapped[int | None] = mapped_column(ForeignKey("campaigns.id"), nullable=True, index=True)
    decision_status: Mapped[DecisionStatus] = mapped_column(SqlEnum(DecisionStatus), nullable=False)
    clearing_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    decision_reason: Mapped[str] = mapped_column(String(64), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    bid_request: Mapped[BidRequest] = relationship(back_populates="auction_decision")
    candidates: Mapped[list["AuctionCandidate"]] = relationship(
        back_populates="auction_decision",
        cascade="all, delete-orphan",
    )


class AuctionCandidate(Base):
    __tablename__ = "auction_candidates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    auction_decision_id: Mapped[int] = mapped_column(ForeignKey("auction_decisions.id"), nullable=False, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    eligibility_status: Mapped[CandidateStatus] = mapped_column(SqlEnum(CandidateStatus), nullable=False)
    rejection_reason: Mapped[str | None] = mapped_column(String(64), nullable=True)
    score: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    auction_decision: Mapped[AuctionDecision] = relationship(back_populates="candidates")
