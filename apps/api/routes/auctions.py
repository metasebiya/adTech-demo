from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.auction_service import AuctionService
from core.permissions.dependencies import require_any_permissions
from core.permissions.roles import RUN_BID_SIMULATIONS, VIEW_AUCTION_TRACES
from core.schemas.auction import AuctionDecisionRead
from infra.db.session import get_db_session

router = APIRouter()


@router.get("", response_model=list[AuctionDecisionRead])
def list_auctions(
    _: Annotated[User, Depends(require_any_permissions(RUN_BID_SIMULATIONS, VIEW_AUCTION_TRACES))],
    session: Session = Depends(get_db_session),
) -> list[AuctionDecisionRead]:
    service = AuctionService(session)
    return [AuctionDecisionRead.model_validate(auction) for auction in service.list_auctions()]


@router.get("/{auction_id}", response_model=AuctionDecisionRead)
def get_auction(
    auction_id: int,
    _: Annotated[User, Depends(require_any_permissions(RUN_BID_SIMULATIONS, VIEW_AUCTION_TRACES))],
    session: Session = Depends(get_db_session),
) -> AuctionDecisionRead:
    service = AuctionService(session)
    return AuctionDecisionRead.model_validate(service.get_auction(auction_id))
