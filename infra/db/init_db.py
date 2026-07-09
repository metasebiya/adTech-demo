from decimal import Decimal

from sqlalchemy.orm import Session

from core.auth.security import hash_password
from core.domain.models import (
    AuctionCandidate,
    AuctionDecision,
    Base,
    BidRequest,
    Campaign,
    CampaignTarget,
    ClickEvent,
    ConversionEvent,
    ImpressionEvent,
    Placement,
    Publisher,
    User,
)
from core.domain.models.auction import CandidateStatus, DecisionStatus
from core.domain.models import Base, Campaign, CampaignTarget, Placement, Publisher, User
from core.domain.models.campaign import CampaignStatus, DeviceType
from core.domain.models.inventory import PlacementStatus, PlacementType, PublisherStatus
from core.domain.models.user import UserRole
from infra.db.session import engine

DEMO_PASSWORD = "ChangeMe123!"


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        seed_demo_users(session)
        seed_demo_inventory(session)
        seed_demo_campaigns(session)
        seed_demo_auction_history(session)


def seed_demo_users(session: Session) -> None:
    if session.query(User).count() > 0:
        return

    users = [
        User(
            email="admin@adtech-demo.local",
            full_name="Amina Tesfaye",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.admin,
            is_active=True,
        ),
        User(
            email="adops@adtech-demo.local",
            full_name="Noah Bennett",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.adops,
            is_active=True,
        ),
        User(
            email="analyst@adtech-demo.local",
            full_name="Maya Okafor",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.analyst,
            is_active=True,
        ),
        User(
            email="viewer@adtech-demo.local",
            full_name="Liam Patel",
            password_hash=hash_password(DEMO_PASSWORD),
            role=UserRole.viewer,
            is_active=True,
        ),
    ]
    session.add_all(users)
    session.commit()


def seed_demo_inventory(session: Session) -> None:
    if session.query(Publisher).count() > 0:
        return

    publishers = [
        Publisher(name="Daily News Network", status=PublisherStatus.active),
        Publisher(name="Pulse Sports Live", status=PublisherStatus.active),
        Publisher(name="CityStyle Mobile", status=PublisherStatus.active),
    ]
    session.add_all(publishers)
    session.flush()

    placements = [
        Placement(
            publisher_id=publishers[0].id,
            name="Homepage Top Banner",
            placement_type=PlacementType.banner,
            status=PlacementStatus.active,
        ),
        Placement(
            publisher_id=publishers[0].id,
            name="Article Inline Native",
            placement_type=PlacementType.native,
            status=PlacementStatus.active,
        ),
        Placement(
            publisher_id=publishers[1].id,
            name="Live Scores Video",
            placement_type=PlacementType.video,
            status=PlacementStatus.active,
        ),
        Placement(
            publisher_id=publishers[2].id,
            name="Mobile App Interstitial",
            placement_type=PlacementType.interstitial,
            status=PlacementStatus.active,
        ),
    ]
    session.add_all(placements)
    session.commit()


def seed_demo_campaigns(session: Session) -> None:
    if session.query(Campaign).count() > 0:
        return

    admin_user = session.query(User).filter(User.email == "admin@adtech-demo.local").one()
    placements = {placement.name: placement for placement in session.query(Placement).all()}

    campaigns = [
        Campaign(
            name="Northwind Homepage Takeover",
            advertiser_name="Northwind Retail",
            status=CampaignStatus.active,
            bid_cpm=Decimal("3.40"),
            daily_budget=Decimal("250.00"),
            remaining_budget=Decimal("182.00"),
            frequency_cap=3,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="US",
                    device_type=DeviceType.desktop,
                    placement_id=placements["Homepage Top Banner"].id,
                )
            ],
        ),
        Campaign(
            name="Contoso Matchday Video Blitz",
            advertiser_name="Contoso Sports",
            status=CampaignStatus.active,
            bid_cpm=Decimal("4.25"),
            daily_budget=Decimal("500.00"),
            remaining_budget=Decimal("418.00"),
            frequency_cap=1,
            frequency_cap=2,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="KE",
                    device_type=DeviceType.mobile,
                    placement_id=placements["Live Scores Video"].id,
                )
            ],
        ),
        Campaign(
            name="Fabrikam Desktop Native Prospecting",
            advertiser_name="Fabrikam Travel",
            status=CampaignStatus.active,
            bid_cpm=Decimal("2.15"),
            daily_budget=Decimal("180.00"),
            remaining_budget=Decimal("140.00"),
            frequency_cap=5,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="US",
                    device_type=DeviceType.desktop,
                    placement_id=placements["Article Inline Native"].id,
                )
            ],
        ),
        Campaign(
            name="Adventure Works Budget Exhausted Mobile",
            advertiser_name="Adventure Works",
            status=CampaignStatus.active,
            bid_cpm=Decimal("2.60"),
            daily_budget=Decimal("80.00"),
            remaining_budget=Decimal("0.00"),
            frequency_cap=1,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="US",
                    device_type=DeviceType.mobile,
                    placement_id=placements["Homepage Top Banner"].id,
                )
            ],
        ),
        Campaign(
            name="Litware Inactive Lifestyle Reach",
            advertiser_name="Litware Living",
            status=CampaignStatus.inactive,
            bid_cpm=Decimal("2.05"),
            daily_budget=Decimal("150.00"),
            remaining_budget=Decimal("140.00"),
            frequency_cap=4,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="US",
                    device_type=DeviceType.desktop,
                    placement_id=placements["Homepage Top Banner"].id,
                )
            ],
        ),
    ]
    session.add_all(campaigns)
    session.commit()


def seed_demo_auction_history(session: Session) -> None:
    if session.query(BidRequest).count() > 0:
        return

    campaigns = {campaign.name: campaign for campaign in session.query(Campaign).all()}
    placements = {placement.name: placement for placement in session.query(Placement).all()}

    history_specs = [
        {
            "placement": "Homepage Top Banner",
            "country": "US",
            "device_type": DeviceType.desktop,
            "user_id": "demo-banner-user-001",
            "winner": "Northwind Homepage Takeover",
            "decision_status": DecisionStatus.win,
            "decision_reason": "Northwind Homepage Takeover",
            "candidates": [
                ("Northwind Homepage Takeover", CandidateStatus.eligible, None, Decimal("3.40")),
                ("Fabrikam Desktop Native Prospecting", CandidateStatus.rejected, "placement_mismatch", None),
                ("Adventure Works Budget Exhausted Mobile", CandidateStatus.rejected, "device_mismatch", None),
                ("Litware Inactive Lifestyle Reach", CandidateStatus.rejected, "inactive", None),
                ("Contoso Matchday Video Blitz", CandidateStatus.rejected, "placement_mismatch", None),
            ],
            "events": {"impression": Decimal("1.45"), "click": True, "conversion": Decimal("24.00")},
        },
        {
            "placement": "Live Scores Video",
            "country": "KE",
            "device_type": DeviceType.mobile,
            "user_id": "freq-cap-user",
            "winner": "Contoso Matchday Video Blitz",
            "decision_status": DecisionStatus.win,
            "decision_reason": "Contoso Matchday Video Blitz",
            "candidates": [
                ("Contoso Matchday Video Blitz", CandidateStatus.eligible, None, Decimal("4.25")),
                ("Northwind Homepage Takeover", CandidateStatus.rejected, "placement_mismatch", None),
                ("Fabrikam Desktop Native Prospecting", CandidateStatus.rejected, "country_mismatch", None),
                ("Adventure Works Budget Exhausted Mobile", CandidateStatus.rejected, "placement_mismatch", None),
                ("Litware Inactive Lifestyle Reach", CandidateStatus.rejected, "inactive", None),
            ],
            "events": {"impression": Decimal("2.10"), "click": True, "conversion": Decimal("18.50")},
        },
        {
            "placement": "Homepage Top Banner",
            "country": "US",
            "device_type": DeviceType.mobile,
            "user_id": "device-mismatch-user-001",
            "winner": None,
            "decision_status": DecisionStatus.no_bid,
            "decision_reason": "no_eligible_campaign",
            "candidates": [
                ("Northwind Homepage Takeover", CandidateStatus.rejected, "device_mismatch", None),
                ("Fabrikam Desktop Native Prospecting", CandidateStatus.rejected, "device_mismatch", None),
                ("Adventure Works Budget Exhausted Mobile", CandidateStatus.rejected, "budget_exhausted", None),
                ("Litware Inactive Lifestyle Reach", CandidateStatus.rejected, "inactive", None),
                ("Contoso Matchday Video Blitz", CandidateStatus.rejected, "placement_mismatch", None),
            ],
            "events": {},
        },
        {
            "placement": "Homepage Top Banner",
            "country": "US",
            "device_type": DeviceType.desktop,
            "user_id": "freq-cap-user",
            "winner": None,
            "decision_status": DecisionStatus.no_bid,
            "decision_reason": "no_eligible_campaign",
            "candidates": [
                ("Northwind Homepage Takeover", CandidateStatus.eligible, None, Decimal("3.40")),
                ("Fabrikam Desktop Native Prospecting", CandidateStatus.rejected, "placement_mismatch", None),
                ("Adventure Works Budget Exhausted Mobile", CandidateStatus.rejected, "device_mismatch", None),
                ("Litware Inactive Lifestyle Reach", CandidateStatus.rejected, "inactive", None),
                ("Contoso Matchday Video Blitz", CandidateStatus.rejected, "frequency_cap_reached", None),
            ],
            "events": {},
        },
        {
            "placement": "Article Inline Native",
            "country": "US",
            "device_type": DeviceType.desktop,
            "user_id": "native-discovery-user-001",
            "winner": "Fabrikam Desktop Native Prospecting",
            "decision_status": DecisionStatus.win,
            "decision_reason": "Fabrikam Desktop Native Prospecting",
            "candidates": [
                ("Fabrikam Desktop Native Prospecting", CandidateStatus.eligible, None, Decimal("2.15")),
                ("Northwind Homepage Takeover", CandidateStatus.rejected, "placement_mismatch", None),
                ("Contoso Matchday Video Blitz", CandidateStatus.rejected, "placement_mismatch", None),
                ("Adventure Works Budget Exhausted Mobile", CandidateStatus.rejected, "budget_exhausted", None),
                ("Litware Inactive Lifestyle Reach", CandidateStatus.rejected, "inactive", None),
            ],
            "events": {"impression": Decimal("1.05"), "click": False, "conversion": None},
        },
    ]

    for spec in history_specs:
        placement = placements[spec["placement"]]
        bid_request = BidRequest(
            publisher_id=placement.publisher_id,
            placement_id=placement.id,
            country=spec["country"],
            device_type=spec["device_type"],
            user_id=spec["user_id"],
        )
        session.add(bid_request)
        session.flush()

        winner = campaigns[spec["winner"]] if spec["winner"] else None
        decision = AuctionDecision(
            bid_request_id=bid_request.id,
            winner_campaign_id=winner.id if winner else None,
            decision_status=spec["decision_status"],
            clearing_price=winner.bid_cpm if winner else None,
            decision_reason=spec["decision_reason"],
            candidates=[
                AuctionCandidate(
                    campaign_id=campaigns[campaign_name].id,
                    eligibility_status=eligibility_status,
                    rejection_reason=rejection_reason,
                    score=score,
                )
                for campaign_name, eligibility_status, rejection_reason, score in spec["candidates"]
            ],
        )
        session.add(decision)
        session.flush()

        events = spec["events"]
        if impression_revenue := events.get("impression"):
            session.add(
                ImpressionEvent(
                    auction_decision_id=decision.id,
                    campaign_id=winner.id,
                    publisher_id=placement.publisher_id,
                    placement_id=placement.id,
                    user_id=bid_request.user_id,
                    revenue=impression_revenue,
                )
            )
        if events.get("click"):
            session.add(ClickEvent(auction_decision_id=decision.id, campaign_id=winner.id))
        if conversion_value := events.get("conversion"):
            session.add(
                ConversionEvent(
                    auction_decision_id=decision.id,
                    campaign_id=winner.id,
                    conversion_value=conversion_value,
                )
            )

    session.commit()
