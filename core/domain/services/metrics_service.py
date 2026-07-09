from __future__ import annotations

from decimal import Decimal

import polars as pl
from sqlalchemy.orm import Session

from core.domain.models import AuctionCandidate, AuctionDecision, BidRequest, Campaign, ClickEvent, ConversionEvent, ImpressionEvent, Publisher
from core.domain.models.auction import CandidateStatus, DecisionStatus
from core.schemas.metrics import (
    CampaignMetricsRow,
    NoBidReasonRow,
    OverviewMetrics,
    PublisherMetricsRow,
    TimeseriesPoint,
)


class MetricsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_overview(self) -> OverviewMetrics:
        bids_df = self._bid_requests_df()
        auctions_df = self._auctions_df()
        impressions_df = self._impressions_df()
        clicks_df = self._clicks_df()
        conversions_df = self._conversions_df()

        bid_requests = bids_df.height
        wins = auctions_df.filter(pl.col("decision_status") == DecisionStatus.win.value).height
        no_bids = auctions_df.filter(pl.col("decision_status") == DecisionStatus.no_bid.value).height
        impressions = impressions_df.height
        clicks = clicks_df.height
        conversions = conversions_df.height
        revenue = self._sum_decimal(impressions_df, "revenue")

        return OverviewMetrics(
            bid_requests=bid_requests,
            wins=wins,
            no_bids=no_bids,
            impressions=impressions,
            clicks=clicks,
            conversions=conversions,
            win_rate=self._safe_rate(wins, bid_requests),
            no_bid_rate=self._safe_rate(no_bids, bid_requests),
            ctr=self._safe_rate(clicks, impressions),
            cvr=self._safe_rate(conversions, clicks),
            revenue=revenue,
        )

    def get_timeseries(self) -> list[TimeseriesPoint]:
        bids_df = self._bid_requests_df()
        auctions_df = self._auctions_df()
        impressions_df = self._impressions_df()
        clicks_df = self._clicks_df()
        conversions_df = self._conversions_df()

        if bids_df.is_empty():
            return []

        bids_daily = bids_df.group_by("date").agg(pl.len().alias("bid_requests"))
        wins_daily = auctions_df.filter(pl.col("decision_status") == DecisionStatus.win.value).group_by("date").agg(pl.len().alias("wins"))
        nobids_daily = auctions_df.filter(pl.col("decision_status") == DecisionStatus.no_bid.value).group_by("date").agg(pl.len().alias("no_bids"))
        impressions_daily = impressions_df.group_by("date").agg(
            pl.len().alias("impressions"),
            pl.col("revenue").sum().alias("revenue"),
        )
        clicks_daily = clicks_df.group_by("date").agg(pl.len().alias("clicks"))
        conversions_daily = conversions_df.group_by("date").agg(pl.len().alias("conversions"))

        merged = (
            bids_daily.join(wins_daily, on="date", how="left")
            .join(nobids_daily, on="date", how="left")
            .join(impressions_daily, on="date", how="left")
            .join(clicks_daily, on="date", how="left")
            .join(conversions_daily, on="date", how="left")
            .fill_null(0)
            .sort("date")
        )

        return [
            TimeseriesPoint(
                date=row["date"],
                bid_requests=int(row["bid_requests"]),
                wins=int(row["wins"]),
                no_bids=int(row["no_bids"]),
                impressions=int(row["impressions"]),
                clicks=int(row["clicks"]),
                conversions=int(row["conversions"]),
                revenue=self._to_decimal(row["revenue"]),
            )
            for row in merged.to_dicts()
        ]

    def get_campaign_metrics(self) -> list[CampaignMetricsRow]:
        campaigns = self.session.query(Campaign).order_by(Campaign.id.asc()).all()
        wins_df = self._auctions_df().filter(pl.col("decision_status") == DecisionStatus.win.value)
        impressions_df = self._impressions_df()
        clicks_df = self._clicks_df()
        conversions_df = self._conversions_df()

        win_counts = self._count_by(wins_df, "winner_campaign_id")
        impression_counts = self._count_by(impressions_df, "campaign_id")
        click_counts = self._count_by(clicks_df, "campaign_id")
        conversion_counts = self._count_by(conversions_df, "campaign_id")
        revenue_by_campaign = self._sum_by(impressions_df, "campaign_id", "revenue")

        rows: list[CampaignMetricsRow] = []
        for campaign in campaigns:
            impressions = impression_counts.get(campaign.id, 0)
            clicks = click_counts.get(campaign.id, 0)
            conversions = conversion_counts.get(campaign.id, 0)
            rows.append(
                CampaignMetricsRow(
                    campaign_id=campaign.id,
                    campaign_name=campaign.name,
                    wins=win_counts.get(campaign.id, 0),
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    revenue=revenue_by_campaign.get(campaign.id, Decimal("0")),
                    ctr=self._safe_rate(clicks, impressions),
                    cvr=self._safe_rate(conversions, clicks),
                )
            )
        return rows

    def get_publisher_metrics(self) -> list[PublisherMetricsRow]:
        publishers = self.session.query(Publisher).order_by(Publisher.id.asc()).all()
        bids_df = self._bid_requests_df()
        impressions_df = self._impressions_df()
        clicks_df = self._clicks_with_publishers_df()
        conversions_df = self._conversions_with_publishers_df()

        bid_counts = self._count_by(bids_df, "publisher_id")
        impression_counts = self._count_by(impressions_df, "publisher_id")
        click_counts = self._count_by(clicks_df, "publisher_id")
        conversion_counts = self._count_by(conversions_df, "publisher_id")
        revenue_by_publisher = self._sum_by(impressions_df, "publisher_id", "revenue")

        rows: list[PublisherMetricsRow] = []
        for publisher in publishers:
            impressions = impression_counts.get(publisher.id, 0)
            clicks = click_counts.get(publisher.id, 0)
            conversions = conversion_counts.get(publisher.id, 0)
            rows.append(
                PublisherMetricsRow(
                    publisher_id=publisher.id,
                    publisher_name=publisher.name,
                    bid_requests=bid_counts.get(publisher.id, 0),
                    impressions=impressions,
                    clicks=clicks,
                    conversions=conversions,
                    revenue=revenue_by_publisher.get(publisher.id, Decimal("0")),
                    ctr=self._safe_rate(clicks, impressions),
                    cvr=self._safe_rate(conversions, clicks),
                )
            )
        return rows

    def get_no_bid_reasons(self) -> list[NoBidReasonRow]:
        candidates = self.session.query(AuctionCandidate).filter(AuctionCandidate.eligibility_status == CandidateStatus.rejected).all()
        if not candidates:
            return []
        reason_df = pl.DataFrame(
            {"reason": [candidate.rejection_reason for candidate in candidates if candidate.rejection_reason]}
        )
        if reason_df.is_empty():
            return []
        counts = reason_df.group_by("reason").agg(pl.len().alias("count")).sort("count", descending=True)
        return [NoBidReasonRow(reason=row["reason"], count=int(row["count"])) for row in counts.to_dicts()]

    def _bid_requests_df(self) -> pl.DataFrame:
        rows = self.session.query(BidRequest).all()
        return pl.DataFrame(
            {
                "id": [row.id for row in rows],
                "publisher_id": [row.publisher_id for row in rows],
                "date": [row.created_at.date() for row in rows],
            }
        ) if rows else pl.DataFrame(schema={"id": pl.Int64, "publisher_id": pl.Int64, "date": pl.Date})

    def _auctions_df(self) -> pl.DataFrame:
        rows = self.session.query(AuctionDecision).all()
        return pl.DataFrame(
            {
                "id": [row.id for row in rows],
                "winner_campaign_id": [row.winner_campaign_id for row in rows],
                "decision_status": [row.decision_status.value for row in rows],
                "decision_reason": [row.decision_reason for row in rows],
                "date": [row.created_at.date() for row in rows],
            }
        ) if rows else pl.DataFrame(
            schema={
                "id": pl.Int64,
                "winner_campaign_id": pl.Int64,
                "decision_status": pl.String,
                "decision_reason": pl.String,
                "date": pl.Date,
            }
        )

    def _impressions_df(self) -> pl.DataFrame:
        rows = self.session.query(ImpressionEvent).all()
        return pl.DataFrame(
            {
                "id": [row.id for row in rows],
                "auction_decision_id": [row.auction_decision_id for row in rows],
                "campaign_id": [row.campaign_id for row in rows],
                "publisher_id": [row.publisher_id for row in rows],
                "revenue": [float(row.revenue) for row in rows],
                "date": [row.created_at.date() for row in rows],
            }
        ) if rows else pl.DataFrame(
            schema={
                "id": pl.Int64,
                "auction_decision_id": pl.Int64,
                "campaign_id": pl.Int64,
                "publisher_id": pl.Int64,
                "revenue": pl.Float64,
                "date": pl.Date,
            }
        )

    def _clicks_df(self) -> pl.DataFrame:
        rows = self.session.query(ClickEvent).all()
        return pl.DataFrame(
            {
                "id": [row.id for row in rows],
                "auction_decision_id": [row.auction_decision_id for row in rows],
                "campaign_id": [row.campaign_id for row in rows],
                "date": [row.created_at.date() for row in rows],
            }
        ) if rows else pl.DataFrame(
            schema={"id": pl.Int64, "auction_decision_id": pl.Int64, "campaign_id": pl.Int64, "date": pl.Date}
        )

    def _conversions_df(self) -> pl.DataFrame:
        rows = self.session.query(ConversionEvent).all()
        return pl.DataFrame(
            {
                "id": [row.id for row in rows],
                "auction_decision_id": [row.auction_decision_id for row in rows],
                "campaign_id": [row.campaign_id for row in rows],
                "conversion_value": [float(row.conversion_value) for row in rows],
                "date": [row.created_at.date() for row in rows],
            }
        ) if rows else pl.DataFrame(
            schema={
                "id": pl.Int64,
                "auction_decision_id": pl.Int64,
                "campaign_id": pl.Int64,
                "conversion_value": pl.Float64,
                "date": pl.Date,
            }
        )

    def _clicks_with_publishers_df(self) -> pl.DataFrame:
        clicks = self.session.query(ClickEvent, BidRequest.publisher_id).join(
            AuctionDecision, ClickEvent.auction_decision_id == AuctionDecision.id
        ).join(BidRequest, AuctionDecision.bid_request_id == BidRequest.id).all()
        return pl.DataFrame(
            {
                "campaign_id": [row[0].campaign_id for row in clicks],
                "publisher_id": [row[1] for row in clicks],
            }
        ) if clicks else pl.DataFrame(schema={"campaign_id": pl.Int64, "publisher_id": pl.Int64})

    def _conversions_with_publishers_df(self) -> pl.DataFrame:
        conversions = self.session.query(ConversionEvent, BidRequest.publisher_id).join(
            AuctionDecision, ConversionEvent.auction_decision_id == AuctionDecision.id
        ).join(BidRequest, AuctionDecision.bid_request_id == BidRequest.id).all()
        return pl.DataFrame(
            {
                "campaign_id": [row[0].campaign_id for row in conversions],
                "publisher_id": [row[1] for row in conversions],
            }
        ) if conversions else pl.DataFrame(schema={"campaign_id": pl.Int64, "publisher_id": pl.Int64})

    @staticmethod
    def _safe_rate(numerator: int, denominator: int) -> float:
        if denominator == 0:
            return 0.0
        return round(numerator / denominator, 4)

    @staticmethod
    def _sum_decimal(df: pl.DataFrame, column: str) -> Decimal:
        if df.is_empty():
            return Decimal("0")
        value = df.select(pl.col(column).sum()).item()
        return MetricsService._to_decimal(value)

    @staticmethod
    def _sum_by(df: pl.DataFrame, group_col: str, value_col: str) -> dict[int, Decimal]:
        if df.is_empty():
            return {}
        grouped = df.group_by(group_col).agg(pl.col(value_col).sum().alias(value_col))
        return {int(row[group_col]): MetricsService._to_decimal(row[value_col]) for row in grouped.to_dicts()}

    @staticmethod
    def _count_by(df: pl.DataFrame, group_col: str) -> dict[int, int]:
        if df.is_empty():
            return {}
        grouped = df.group_by(group_col).agg(pl.len().alias("count"))
        return {int(row[group_col]): int(row["count"]) for row in grouped.to_dicts() if row[group_col] is not None}

    @staticmethod
    def _to_decimal(value: float | int | None) -> Decimal:
        if value is None:
            return Decimal("0")
        return Decimal(str(round(float(value), 2)))
