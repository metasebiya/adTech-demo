from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.auction_service import AuctionService
from core.permissions.dependencies import require_permissions
from core.permissions.roles import RUN_BID_SIMULATIONS
from core.schemas.auction import AuctionDecisionRead, BidRequestAuctionResponse, BidRequestCreate, BidRequestRead
from infra.db.session import get_db_session

router = APIRouter()


@router.post("", response_model=BidRequestAuctionResponse, status_code=201)
def create_bid_request(
    payload: BidRequestCreate,
    _: Annotated[User, Depends(require_permissions(RUN_BID_SIMULATIONS))],
    session: Session = Depends(get_db_session),
) -> BidRequestAuctionResponse:
    service = AuctionService(session)
    bid_request, auction = service.run_bid_request(payload)
    return BidRequestAuctionResponse(
        bid_request=BidRequestRead.model_validate(bid_request),
        auction_decision=AuctionDecisionRead.model_validate(auction),
    )
