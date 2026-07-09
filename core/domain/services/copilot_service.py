from __future__ import annotations

import re
from decimal import Decimal

from sqlalchemy.orm import Session

from core.domain.models import AuctionDecision, Campaign, ImpressionEvent
from core.domain.models.auction import CandidateStatus, DecisionStatus
from core.domain.services.metrics_service import MetricsService
from core.schemas.copilot import CopilotQueryResponse, CopilotSuggestedQuestion


class CopilotService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.metrics_service = MetricsService(session)

    def get_suggested_questions(self) -> list[CopilotSuggestedQuestion]:
        return [
            CopilotSuggestedQuestion(category="auction", question="Why did auction 1 select its winning campaign?"),
            CopilotSuggestedQuestion(category="auction", question="Explain the latest no-bid pattern in the marketplace."),
            CopilotSuggestedQuestion(category="analytics", question="Summarize current performance across win rate, CTR, CVR, and revenue."),
            CopilotSuggestedQuestion(category="campaign", question="Which campaign is performing best right now and why?"),
            CopilotSuggestedQuestion(category="operations", question="What should ad ops change next to reduce no-bids?"),
        ]

    def answer_query(self, query: str) -> CopilotQueryResponse:
        normalized = " ".join(query.strip().lower().split())
        if not normalized:
            normalized = "summarize current performance"

        if auction_id := self._extract_auction_id(normalized):
            return self._explain_auction(auction_id)

        if any(token in normalized for token in {"no-bid", "no bid", "rejected", "rejection"}):
            return self._explain_no_bid_patterns()

        matched_campaign = self._match_campaign(normalized)
        if matched_campaign is not None:
            return self._explain_campaign(matched_campaign)

        if any(token in normalized for token in {"campaign", "best performing", "top campaign"}):
            top_campaign = self._top_campaign()
            if top_campaign is not None:
                return self._explain_campaign(top_campaign)

        return self._summarize_analytics()

    def _explain_auction(self, auction_id: int) -> CopilotQueryResponse:
        auction = self.session.query(AuctionDecision).filter(AuctionDecision.id == auction_id).one_or_none()
        if auction is None:
            return CopilotQueryResponse(
                mode="auction_lookup",
                title=f"Auction {auction_id} Not Found",
                answer="I could not find that auction in the current demo dataset.",
                supporting_facts=["No matching auction record exists in the current seeded or simulated history."],
                recommended_actions=["Open Auction Trace Viewer and select an available auction ID."],
                inspected_sources=["auction_decisions"],
            )

        eligible = [candidate for candidate in auction.candidates if candidate.eligibility_status == CandidateStatus.eligible]
        rejected = [candidate for candidate in auction.candidates if candidate.eligibility_status == CandidateStatus.rejected]

        if auction.decision_status == DecisionStatus.win:
            answer = (
                f"Auction {auction.id} resulted in a win because campaign {auction.winner_campaign_id} "
                f"was eligible and had the strongest clearing bid at {self._format_money(auction.clearing_price)}."
            )
            recommendations = [
                "Use Auction Trace Viewer to show the rejected candidates and their exact rejection reasons.",
                "Compare this winner against current metrics to explain downstream delivery impact.",
            ]
        else:
            answer = (
                f"Auction {auction.id} resulted in no-bid because no campaign cleared eligibility. "
                f"The decision reason recorded was `{auction.decision_reason}`."
            )
            recommendations = [
                "Inspect the dominant rejection reason to see whether targeting, budget, or frequency cap blocked demand.",
                "Use the Bid Simulator to test a nearby scenario with different device, country, or user frequency state.",
            ]

        supporting_facts = [
            f"Decision status: {auction.decision_status.value}",
            f"Eligible candidates: {len(eligible)}",
            f"Rejected candidates: {len(rejected)}",
        ]
        supporting_facts.extend(
            f"Campaign {candidate.campaign_id} rejected due to {candidate.rejection_reason}."
            for candidate in rejected[:3]
            if candidate.rejection_reason
        )
        if auction.clearing_price is not None:
            supporting_facts.append(f"Clearing price: {self._format_money(auction.clearing_price)}")

        return CopilotQueryResponse(
            mode="auction_explanation",
            title=f"Auction {auction.id} Explanation",
            answer=answer,
            supporting_facts=supporting_facts,
            recommended_actions=recommendations,
            inspected_sources=["auction_decisions", "auction_candidates", "bid_requests"],
        )

    def _explain_no_bid_patterns(self) -> CopilotQueryResponse:
        no_bid_rows = self.metrics_service.get_no_bid_reasons()
        latest_no_bid = (
            self.session.query(AuctionDecision)
            .filter(AuctionDecision.decision_status == DecisionStatus.no_bid)
            .order_by(AuctionDecision.created_at.desc())
            .first()
        )
        if not no_bid_rows:
            return CopilotQueryResponse(
                mode="no_bid_analysis",
                title="No No-Bid History Yet",
                answer="The current dataset does not contain rejected candidates yet, so there is no no-bid pattern to summarize.",
                supporting_facts=["No rejected candidate rows were found in the current auction history."],
                recommended_actions=["Run a no-bid scenario in the Bid Simulator to generate rejection data."],
                inspected_sources=["auction_candidates", "auction_decisions"],
            )

        top_reason = no_bid_rows[0]
        answer = (
            f"The leading no-bid driver right now is `{top_reason.reason}`, which appears {top_reason.count} times "
            f"across rejected candidate evaluations."
        )
        facts = [f"{row.reason}: {row.count} rejected candidate records" for row in no_bid_rows[:4]]
        if latest_no_bid is not None:
            facts.append(f"Latest no-bid auction: {latest_no_bid.id}")

        recommendations = []
        if top_reason.reason == "device_mismatch":
            recommendations.append("Review device targeting for active campaigns on the placements generating the most traffic.")
        if top_reason.reason == "budget_exhausted":
            recommendations.append("Increase remaining budget or shift spend from underperforming campaigns.")
        if top_reason.reason == "frequency_cap_reached":
            recommendations.append("Evaluate whether current frequency caps are limiting monetization too aggressively.")
        if top_reason.reason == "placement_mismatch":
            recommendations.append("Add active campaign targets for the affected placements.")
        if not recommendations:
            recommendations.append("Inspect recent auction traces to verify whether targeting logic or campaign state is the main blocker.")

        return CopilotQueryResponse(
            mode="no_bid_analysis",
            title="No-Bid Pattern Summary",
            answer=answer,
            supporting_facts=facts,
            recommended_actions=recommendations,
            inspected_sources=["auction_candidates", "auction_decisions", "metrics.no_bid_reasons"],
        )

    def _explain_campaign(self, campaign: Campaign) -> CopilotQueryResponse:
        campaign_metrics = next(
            (row for row in self.metrics_service.get_campaign_metrics() if row.campaign_id == campaign.id),
            None,
        )
        if campaign_metrics is None:
            return self._summarize_analytics()

        answer = (
            f"Campaign `{campaign.name}` currently has {campaign_metrics.wins} wins, "
            f"{campaign_metrics.impressions} impressions, {campaign_metrics.clicks} clicks, "
            f"and {self._format_money(campaign_metrics.revenue)} in attributed revenue."
        )
        facts = [
            f"Status: {campaign.status.value}",
            f"Bid CPM: {self._format_money(campaign.bid_cpm)}",
            f"Remaining budget: {self._format_money(campaign.remaining_budget)}",
            f"CTR: {campaign_metrics.ctr:.2%}",
            f"CVR: {campaign_metrics.cvr:.2%}",
        ]
        recommendations = [
            "Compare this campaign against the Auction Trace Viewer to show where it wins or gets rejected.",
            "Review remaining budget and targeting if the campaign should be winning more often.",
        ]
        return CopilotQueryResponse(
            mode="campaign_analysis",
            title=f"Campaign Insight: {campaign.name}",
            answer=answer,
            supporting_facts=facts,
            recommended_actions=recommendations,
            inspected_sources=["campaigns", "campaign_targets", "metrics.campaigns"],
        )

    def _summarize_analytics(self) -> CopilotQueryResponse:
        overview = self.metrics_service.get_overview()
        top_campaign = self._top_campaign()
        top_publisher = max(
            self.metrics_service.get_publisher_metrics(),
            key=lambda row: (row.revenue, row.bid_requests),
            default=None,
        )

        answer = (
            f"The marketplace currently shows {overview.bid_requests} bid requests, {overview.wins} wins, "
            f"{overview.impressions} impressions, and {self._format_money(overview.revenue)} in revenue. "
            f"Win rate is {overview.win_rate:.2%}, CTR is {overview.ctr:.2%}, and CVR is {overview.cvr:.2%}."
        )
        facts = [
            f"No-bids: {overview.no_bids}",
            f"Clicks: {overview.clicks}",
            f"Conversions: {overview.conversions}",
        ]
        if top_campaign is not None:
            facts.append(f"Top campaign by seeded delivery: {top_campaign.name}")
        if top_publisher is not None:
            facts.append(f"Top publisher by revenue: {top_publisher.publisher_name}")

        recommendations = [
            "Use the Analytics Dashboard to compare campaign and publisher trends visually.",
            "Open the Bid Simulator to demonstrate how operational changes affect auction outcomes.",
        ]
        return CopilotQueryResponse(
            mode="analytics_summary",
            title="Marketplace Performance Summary",
            answer=answer,
            supporting_facts=facts,
            recommended_actions=recommendations,
            inspected_sources=["metrics.overview", "metrics.campaigns", "metrics.publishers"],
        )

    def _extract_auction_id(self, query: str) -> int | None:
        match = re.search(r"auction\s+(\d+)", query)
        return int(match.group(1)) if match else None

    def _match_campaign(self, query: str) -> Campaign | None:
        campaigns = self.session.query(Campaign).order_by(Campaign.id.asc()).all()
        for campaign in campaigns:
            if campaign.name.lower() in query:
                return campaign
        return None

    def _top_campaign(self) -> Campaign | None:
        campaign_rows = self.metrics_service.get_campaign_metrics()
        if not campaign_rows:
            return None
        top_row = max(campaign_rows, key=lambda row: (row.revenue, row.wins, row.impressions))
        return self.session.query(Campaign).filter(Campaign.id == top_row.campaign_id).one_or_none()

    @staticmethod
    def _format_money(value: Decimal | None) -> str:
        amount = Decimal("0") if value is None else Decimal(str(value))
        return f"${amount:,.2f}"
