from datetime import date
from decimal import Decimal

from pydantic import BaseModel


class OverviewMetrics(BaseModel):
    bid_requests: int
    wins: int
    no_bids: int
    impressions: int
    clicks: int
    conversions: int
    win_rate: float
    no_bid_rate: float
    ctr: float
    cvr: float
    revenue: Decimal


class TimeseriesPoint(BaseModel):
    date: date
    bid_requests: int
    wins: int
    no_bids: int
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal


class CampaignMetricsRow(BaseModel):
    campaign_id: int
    campaign_name: str
    wins: int
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    ctr: float
    cvr: float


class PublisherMetricsRow(BaseModel):
    publisher_id: int
    publisher_name: str
    bid_requests: int
    impressions: int
    clicks: int
    conversions: int
    revenue: Decimal
    ctr: float
    cvr: float


class NoBidReasonRow(BaseModel):
    reason: str
    count: int
