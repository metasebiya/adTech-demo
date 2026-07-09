from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SqlEnum, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.domain.models.base import Base


class PublisherStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class PlacementStatus(str, Enum):
    active = "active"
    inactive = "inactive"


class PlacementType(str, Enum):
    banner = "banner"
    video = "video"
    native = "native"
    interstitial = "interstitial"


class Publisher(Base):
    __tablename__ = "publishers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    status: Mapped[PublisherStatus] = mapped_column(
        SqlEnum(PublisherStatus),
        default=PublisherStatus.active,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    placements: Mapped[list["Placement"]] = relationship(
        back_populates="publisher",
        cascade="all, delete-orphan",
    )


class Placement(Base):
    __tablename__ = "placements"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    publisher_id: Mapped[int] = mapped_column(ForeignKey("publishers.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    placement_type: Mapped[PlacementType] = mapped_column(SqlEnum(PlacementType), nullable=False)
    status: Mapped[PlacementStatus] = mapped_column(
        SqlEnum(PlacementStatus),
        default=PlacementStatus.active,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    publisher: Mapped[Publisher] = relationship(back_populates="placements")
