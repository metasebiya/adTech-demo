from sqlalchemy.orm import Session, joinedload

from core.domain.models.auction import AuctionDecision, BidRequest


class BidRequestRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, bid_request: BidRequest) -> BidRequest:
        self.session.add(bid_request)
        self.session.flush()
        self.session.refresh(bid_request)
        return bid_request


class AuctionDecisionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, decision: AuctionDecision) -> AuctionDecision:
        self.session.add(decision)
        self.session.commit()
        self.session.refresh(decision)
        return self.get_by_id(decision.id) or decision

    def list_all(self) -> list[AuctionDecision]:
        return (
            self.session.query(AuctionDecision)
            .options(
                joinedload(AuctionDecision.bid_request),
                joinedload(AuctionDecision.candidates),
            )
            .order_by(AuctionDecision.id.desc())
            .all()
        )

    def get_by_id(self, auction_id: int) -> AuctionDecision | None:
        return (
            self.session.query(AuctionDecision)
            .options(
                joinedload(AuctionDecision.bid_request),
                joinedload(AuctionDecision.candidates),
            )
            .filter(AuctionDecision.id == auction_id)
            .one_or_none()
        )
