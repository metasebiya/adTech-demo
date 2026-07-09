from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.metrics_service import MetricsService
from core.permissions.dependencies import require_any_permissions
from core.schemas.metrics import (
    CampaignMetricsRow,
    NoBidReasonRow,
    OverviewMetrics,
    PublisherMetricsRow,
    TimeseriesPoint,
)
from infra.db.session import get_db_session

router = APIRouter()


@router.get("/overview", response_model=OverviewMetrics)
def get_overview(
    _: Annotated[User, Depends(require_any_permissions("view_analytics", "view_dashboard"))],
    session: Session = Depends(get_db_session),
) -> OverviewMetrics:
    return MetricsService(session).get_overview()


@router.get("/timeseries", response_model=list[TimeseriesPoint])
def get_timeseries(
    _: Annotated[User, Depends(require_any_permissions("view_analytics", "view_dashboard"))],
    session: Session = Depends(get_db_session),
) -> list[TimeseriesPoint]:
    return MetricsService(session).get_timeseries()


@router.get("/campaigns", response_model=list[CampaignMetricsRow])
def get_campaign_metrics(
    _: Annotated[User, Depends(require_any_permissions("view_analytics", "view_dashboard"))],
    session: Session = Depends(get_db_session),
) -> list[CampaignMetricsRow]:
    return MetricsService(session).get_campaign_metrics()


@router.get("/publishers", response_model=list[PublisherMetricsRow])
def get_publisher_metrics(
    _: Annotated[User, Depends(require_any_permissions("view_analytics", "view_dashboard"))],
    session: Session = Depends(get_db_session),
) -> list[PublisherMetricsRow]:
    return MetricsService(session).get_publisher_metrics()


@router.get("/no-bid-reasons", response_model=list[NoBidReasonRow])
def get_no_bid_reasons(
    _: Annotated[User, Depends(require_any_permissions("view_analytics", "view_dashboard"))],
    session: Session = Depends(get_db_session),
) -> list[NoBidReasonRow]:
    return MetricsService(session).get_no_bid_reasons()
