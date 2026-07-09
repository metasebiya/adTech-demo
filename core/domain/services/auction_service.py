from dataclasses import dataclass
from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.domain.models.auction import (
    AuctionCandidate,
    AuctionDecision,
    BidRequest,
    CandidateStatus,
    DecisionStatus,
    RejectionReason,
)
from core.domain.models.campaign import Campaign, CampaignStatus
from core.domain.models.inventory import Placement, Publisher
from core.schemas.auction import BidRequestCreate
from infra.repositories.auction_repository import AuctionDecisionRepository, BidRequestRepository
from infra.repositories.campaign_repository import CampaignRepository
from infra.repositories.inventory_repository import PlacementRepository, PublisherRepository


@dataclass
class CandidateEvaluation:
    campaign: Campaign
    status: CandidateStatus
    rejection_reason: RejectionReason | None
    score: Decimal | None


class AuctionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.bid_request_repository = BidRequestRepository(session)
        self.auction_repository = AuctionDecisionRepository(session)
        self.campaign_repository = CampaignRepository(session)
        self.publisher_repository = PublisherRepository(session)
        self.placement_repository = PlacementRepository(session)

    def run_bid_request(self, payload: BidRequestCreate) -> tuple[BidRequest, AuctionDecision]:
        self._validate_inventory(payload.publisher_id, payload.placement_id)
        bid_request = self.bid_request_repository.create(
            BidRequest(
                publisher_id=payload.publisher_id,
                placement_id=payload.placement_id,
                country=payload.country.strip().upper(),
                device_type=payload.device_type,
                user_id=payload.user_id.strip(),
            )
        )
        evaluations = [self._evaluate_campaign(campaign, bid_request) for campaign in self.campaign_repository.list_all()]
        decision = self._build_decision(bid_request, evaluations)
        saved = self.auction_repository.create(decision)
        return bid_request, saved

    def list_auctions(self) -> list[AuctionDecision]:
        return self.auction_repository.list_all()

    def get_auction(self, auction_id: int) -> AuctionDecision:
        auction = self.auction_repository.get_by_id(auction_id)
        if auction is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Auction not found")
        return auction

    def _validate_inventory(self, publisher_id: int, placement_id: int) -> tuple[Publisher, Placement]:
        publisher = self.publisher_repository.get_by_id(publisher_id)
        if publisher is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Publisher not found")
        placement = self.placement_repository.get_by_id(placement_id)
        if placement is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Placement not found")
        if placement.publisher_id != publisher.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Placement does not belong to publisher",
            )
        return publisher, placement

    def _evaluate_campaign(self, campaign: Campaign, bid_request: BidRequest) -> CandidateEvaluation:
        if campaign.status != CampaignStatus.active:
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.inactive, None)

        matching_placement_targets = [target for target in campaign.targets if target.placement_id == bid_request.placement_id]
        if not matching_placement_targets:
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.placement_mismatch, None)

        matching_country_targets = [
            target for target in matching_placement_targets if target.country.upper() == bid_request.country.upper()
        ]
        if not matching_country_targets:
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.country_mismatch, None)

        matching_device_targets = [
            target for target in matching_country_targets if target.device_type == bid_request.device_type
        ]
        if not matching_device_targets:
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.device_mismatch, None)

        if campaign.remaining_budget <= Decimal("0"):
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.budget_exhausted, None)

        if self._frequency_cap_reached(campaign.id, bid_request.user_id):
            return CandidateEvaluation(campaign, CandidateStatus.rejected, RejectionReason.frequency_cap_reached, None)

        return CandidateEvaluation(campaign, CandidateStatus.eligible, None, campaign.bid_cpm)

    def _frequency_cap_reached(self, campaign_id: int, request_user_id: str) -> bool:
        prior_wins = 0
        for auction in self.auction_repository.list_all():
            if auction.winner_campaign_id != campaign_id or auction.bid_request.user_id != request_user_id:
                continue
            prior_wins += 1
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if campaign is None:
            return False
        return prior_wins >= campaign.frequency_cap

    def _build_decision(
        self,
        bid_request: BidRequest,
        evaluations: list[CandidateEvaluation],
    ) -> AuctionDecision:
        eligible = [evaluation for evaluation in evaluations if evaluation.status == CandidateStatus.eligible]
        winner = max(eligible, key=lambda item: item.score or Decimal("0")) if eligible else None

        decision = AuctionDecision(
            bid_request_id=bid_request.id,
            winner_campaign_id=winner.campaign.id if winner else None,
            decision_status=DecisionStatus.win if winner else DecisionStatus.no_bid,
            clearing_price=winner.score if winner else None,
            decision_reason=winner.campaign.name if winner else RejectionReason.no_eligible_campaign.value,
        )
        decision.candidates = [
            AuctionCandidate(
                campaign_id=evaluation.campaign.id,
                eligibility_status=evaluation.status,
                rejection_reason=evaluation.rejection_reason.value if evaluation.rejection_reason else None,
                score=evaluation.score,
            )
            for evaluation in evaluations
        ]
        return decision
