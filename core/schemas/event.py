from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class ImpressionEventCreate(BaseModel):
    auction_decision_id: int
    campaign_id: int
    publisher_id: int
    placement_id: int
    user_id: str = Field(min_length=1, max_length=255)
    revenue: Decimal = Field(ge=0)


class ClickEventCreate(BaseModel):
    auction_decision_id: int
    campaign_id: int


class ConversionEventCreate(BaseModel):
    auction_decision_id: int
    campaign_id: int
    conversion_value: Decimal = Field(ge=0)


class ImpressionEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auction_decision_id: int
    campaign_id: int
    publisher_id: int
    placement_id: int
    user_id: str
    revenue: Decimal
    created_at: datetime


class ClickEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auction_decision_id: int
    campaign_id: int
    created_at: datetime


class ConversionEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    auction_decision_id: int
    campaign_id: int
    conversion_value: Decimal
    created_at: datetime


class EventListItem(BaseModel):
    event_type: Literal["impression", "click", "conversion"]
    event_id: int
    auction_decision_id: int
    campaign_id: int
    publisher_id: int | None = None
    placement_id: int | None = None
    user_id: str | None = None
    revenue: Decimal | None = None
    conversion_value: Decimal | None = None
    created_at: datetime
