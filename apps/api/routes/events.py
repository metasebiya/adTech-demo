from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.event_service import EventService
from core.permissions.dependencies import require_any_permissions, require_permissions
from core.schemas.event import (
    ClickEventCreate,
    ClickEventRead,
    ConversionEventCreate,
    ConversionEventRead,
    EventListItem,
    ImpressionEventCreate,
    ImpressionEventRead,
)
from infra.db.session import get_db_session

router = APIRouter()


@router.post("/impression", response_model=ImpressionEventRead, status_code=201)
def create_impression(
    payload: ImpressionEventCreate,
    _: Annotated[User, Depends(require_permissions("log_events"))],
    session: Session = Depends(get_db_session),
) -> ImpressionEventRead:
    service = EventService(session)
    return ImpressionEventRead.model_validate(service.create_impression(payload))


@router.post("/click", response_model=ClickEventRead, status_code=201)
def create_click(
    payload: ClickEventCreate,
    _: Annotated[User, Depends(require_permissions("log_events"))],
    session: Session = Depends(get_db_session),
) -> ClickEventRead:
    service = EventService(session)
    return ClickEventRead.model_validate(service.create_click(payload))


@router.post("/conversion", response_model=ConversionEventRead, status_code=201)
def create_conversion(
    payload: ConversionEventCreate,
    _: Annotated[User, Depends(require_permissions("log_events"))],
    session: Session = Depends(get_db_session),
) -> ConversionEventRead:
    service = EventService(session)
    return ConversionEventRead.model_validate(service.create_conversion(payload))


@router.get("", response_model=list[EventListItem])
def list_events(
    _: Annotated[User, Depends(require_any_permissions("log_events", "view_events"))],
    session: Session = Depends(get_db_session),
    campaign_id: int | None = Query(default=None),
    auction_decision_id: int | None = Query(default=None),
    publisher_id: int | None = Query(default=None),
) -> list[EventListItem]:
    service = EventService(session)
    return service.list_events(
        campaign_id=campaign_id,
        auction_decision_id=auction_decision_id,
        publisher_id=publisher_id,
    )
