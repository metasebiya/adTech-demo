from datetime import datetime

from pydantic import BaseModel, ConfigDict

from core.domain.models.inventory import PlacementStatus, PlacementType, PublisherStatus


class PublisherCreate(BaseModel):
    name: str
    status: PublisherStatus = PublisherStatus.active


class PublisherRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    status: PublisherStatus
    created_at: datetime


class PlacementCreate(BaseModel):
    publisher_id: int
    name: str
    placement_type: PlacementType
    status: PlacementStatus = PlacementStatus.active


class PlacementRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    publisher_id: int
    name: str
    placement_type: PlacementType
    status: PlacementStatus
    created_at: datetime
