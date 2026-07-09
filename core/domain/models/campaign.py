from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.domain.models.base import Base


class CampaignStatus(str, Enum):
    draft = "draft"
    active = "active"
    inactive = "inactive"


class DeviceType(str, Enum):
    desktop = "desktop"
    mobile = "mobile"
    tablet = "tablet"
    ctv = "ctv"


class Campaign(Base):
    __tablename__ = "campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    advertiser_name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[CampaignStatus] = mapped_column(
        SqlEnum(CampaignStatus),
        default=CampaignStatus.draft,
        nullable=False,
    )
    bid_cpm: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    daily_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    remaining_budget: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    frequency_cap: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    targets: Mapped[list["CampaignTarget"]] = relationship(
        back_populates="campaign",
        cascade="all, delete-orphan",
    )


class CampaignTarget(Base):
    __tablename__ = "campaign_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    campaign_id: Mapped[int] = mapped_column(ForeignKey("campaigns.id"), nullable=False, index=True)
    country: Mapped[str] = mapped_column(String(8), nullable=False)
    device_type: Mapped[DeviceType] = mapped_column(SqlEnum(DeviceType), nullable=False)
    placement_id: Mapped[int] = mapped_column(ForeignKey("placements.id"), nullable=False, index=True)
    campaign: Mapped[Campaign] = relationship(back_populates="targets")
