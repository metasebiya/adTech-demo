from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.domain.models.auction import AuctionDecision, DecisionStatus
from core.domain.models.event import ClickEvent, ConversionEvent, ImpressionEvent
from core.schemas.event import (
    ClickEventCreate,
    ConversionEventCreate,
    EventListItem,
    ImpressionEventCreate,
)
from infra.repositories.auction_repository import AuctionDecisionRepository
from infra.repositories.event_repository import (
    ClickEventRepository,
    ConversionEventRepository,
    ImpressionEventRepository,
)


class EventService:
    def __init__(self, session: Session) -> None:
        self.auction_repository = AuctionDecisionRepository(session)
        self.impression_repository = ImpressionEventRepository(session)
        self.click_repository = ClickEventRepository(session)
        self.conversion_repository = ConversionEventRepository(session)

    def create_impression(self, payload: ImpressionEventCreate) -> ImpressionEvent:
        decision = self._validate_winning_auction(payload.auction_decision_id, payload.campaign_id)
        bid_request = decision.bid_request
        if payload.publisher_id != bid_request.publisher_id or payload.placement_id != bid_request.placement_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impression inventory does not match auction decision",
            )
        if payload.user_id.strip() != bid_request.user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Impression user does not match auction decision",
            )
        event = ImpressionEvent(
            auction_decision_id=payload.auction_decision_id,
            campaign_id=payload.campaign_id,
            publisher_id=payload.publisher_id,
            placement_id=payload.placement_id,
            user_id=payload.user_id.strip(),
            revenue=payload.revenue,
        )
        return self.impression_repository.create(event)

    def create_click(self, payload: ClickEventCreate) -> ClickEvent:
        self._validate_winning_auction(payload.auction_decision_id, payload.campaign_id)
        event = ClickEvent(
            auction_decision_id=payload.auction_decision_id,
            campaign_id=payload.campaign_id,
        )
        return self.click_repository.create(event)

    def create_conversion(self, payload: ConversionEventCreate) -> ConversionEvent:
        self._validate_winning_auction(payload.auction_decision_id, payload.campaign_id)
        event = ConversionEvent(
            auction_decision_id=payload.auction_decision_id,
            campaign_id=payload.campaign_id,
            conversion_value=payload.conversion_value,
        )
        return self.conversion_repository.create(event)

    def list_events(
        self,
        campaign_id: int | None = None,
        auction_decision_id: int | None = None,
        publisher_id: int | None = None,
    ) -> list[EventListItem]:
        events: list[EventListItem] = []
        decision_publisher_map = {
            auction.id: auction.bid_request.publisher_id for auction in self.auction_repository.list_all()
        }
        for impression in self.impression_repository.list_all():
            if campaign_id is not None and impression.campaign_id != campaign_id:
                continue
            if auction_decision_id is not None and impression.auction_decision_id != auction_decision_id:
                continue
            if publisher_id is not None and impression.publisher_id != publisher_id:
                continue
            events.append(
                EventListItem(
                    event_type="impression",
                    event_id=impression.id,
                    auction_decision_id=impression.auction_decision_id,
                    campaign_id=impression.campaign_id,
                    publisher_id=impression.publisher_id,
                    placement_id=impression.placement_id,
                    user_id=impression.user_id,
                    revenue=impression.revenue,
                    created_at=impression.created_at,
                )
            )
        for click in self.click_repository.list_all():
            if campaign_id is not None and click.campaign_id != campaign_id:
                continue
            if auction_decision_id is not None and click.auction_decision_id != auction_decision_id:
                continue
            if publisher_id is not None and decision_publisher_map.get(click.auction_decision_id) != publisher_id:
                continue
            events.append(
                EventListItem(
                    event_type="click",
                    event_id=click.id,
                    auction_decision_id=click.auction_decision_id,
                    campaign_id=click.campaign_id,
                    created_at=click.created_at,
                )
            )
        for conversion in self.conversion_repository.list_all():
            if campaign_id is not None and conversion.campaign_id != campaign_id:
                continue
            if auction_decision_id is not None and conversion.auction_decision_id != auction_decision_id:
                continue
            if publisher_id is not None and decision_publisher_map.get(conversion.auction_decision_id) != publisher_id:
                continue
            events.append(
                EventListItem(
                    event_type="conversion",
                    event_id=conversion.id,
                    auction_decision_id=conversion.auction_decision_id,
                    campaign_id=conversion.campaign_id,
                    conversion_value=conversion.conversion_value,
                    created_at=conversion.created_at,
                )
            )
        return sorted(events, key=lambda item: item.created_at, reverse=True)

    def _validate_winning_auction(self, auction_decision_id: int, campaign_id: int) -> AuctionDecision:
        decision = self.auction_repository.get_by_id(auction_decision_id)
        if decision is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction decision not found")
        if decision.decision_status != DecisionStatus.win or decision.winner_campaign_id != campaign_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event must reference the winning campaign for a winning auction",
            )
        return decision
