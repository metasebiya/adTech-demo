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
    Placement,
    Publisher,
    User,
)
from core.domain.models.auction import CandidateStatus, DecisionStatus
from core.domain.models.campaign import CampaignStatus, DeviceType
from core.domain.models.inventory import PlacementStatus, PlacementType, PublisherStatus
from core.domain.models.user import UserRole
from infra.db.session import engine


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
            full_name="Admin User",
            password_hash=hash_password("ChangeMe123!"),
            role=UserRole.admin,
            is_active=True,
        ),
        User(
            email="adops@adtech-demo.local",
            full_name="AdOps User",
            password_hash=hash_password("ChangeMe123!"),
            role=UserRole.adops,
            is_active=True,
        ),
        User(
            email="analyst@adtech-demo.local",
            full_name="Analyst User",
            password_hash=hash_password("ChangeMe123!"),
            role=UserRole.analyst,
            is_active=True,
        ),
        User(
            email="viewer@adtech-demo.local",
            full_name="Viewer User",
            password_hash=hash_password("ChangeMe123!"),
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
        Publisher(name="Sports Flash Media", status=PublisherStatus.active),
        Publisher(name="Lifestyle Hub", status=PublisherStatus.inactive),
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
            status=PlacementStatus.inactive,
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
            name="US Homepage Banner Push",
            advertiser_name="Northwind Retail",
            status=CampaignStatus.active,
            bid_cpm=Decimal("3.25"),
            daily_budget=Decimal("250.00"),
            remaining_budget=Decimal("175.50"),
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
            name="Sports Video Reach",
            advertiser_name="Contoso Sports",
            status=CampaignStatus.active,
            bid_cpm=Decimal("4.10"),
            daily_budget=Decimal("500.00"),
            remaining_budget=Decimal("420.00"),
            frequency_cap=1,
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
            name="Native Discovery Test",
            advertiser_name="Fabrikam Travel",
            status=CampaignStatus.draft,
            bid_cpm=Decimal("1.80"),
            daily_budget=Decimal("120.00"),
            remaining_budget=Decimal("120.00"),
            frequency_cap=5,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="UK",
                    device_type=DeviceType.desktop,
                    placement_id=placements["Article Inline Native"].id,
                )
            ],
        ),
        Campaign(
            name="Budget Exhausted Mobile Burst",
            advertiser_name="Adventure Works",
            status=CampaignStatus.active,
            bid_cpm=Decimal("2.50"),
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
            name="Paused Lifestyle Awareness",
            advertiser_name="Litware Living",
            status=CampaignStatus.inactive,
            bid_cpm=Decimal("2.05"),
            daily_budget=Decimal("150.00"),
            remaining_budget=Decimal("140.00"),
            frequency_cap=4,
            created_by_user_id=admin_user.id,
            targets=[
                CampaignTarget(
                    country="CA",
                    device_type=DeviceType.tablet,
                    placement_id=placements["Mobile App Interstitial"].id,
                )
            ],
        ),
    ]
    session.add_all(campaigns)
    session.commit()


def seed_demo_auction_history(session: Session) -> None:
    if session.query(BidRequest).count() > 0:
        return

    sports_campaign = session.query(Campaign).filter(Campaign.name == "Sports Video Reach").one()
    placement = session.query(Placement).filter(Placement.name == "Live Scores Video").one()
    publisher_id = placement.publisher_id

    bid_request = BidRequest(
        publisher_id=publisher_id,
        placement_id=placement.id,
        country="KE",
        device_type=DeviceType.mobile,
        user_id="freq-cap-user",
    )
    session.add(bid_request)
    session.flush()

    decision = AuctionDecision(
        bid_request_id=bid_request.id,
        winner_campaign_id=sports_campaign.id,
        decision_status=DecisionStatus.win,
        clearing_price=sports_campaign.bid_cpm,
        decision_reason=sports_campaign.name,
        candidates=[
            AuctionCandidate(
                campaign_id=sports_campaign.id,
                eligibility_status=CandidateStatus.eligible,
                rejection_reason=None,
                score=sports_campaign.bid_cpm,
            )
        ],
    )
    session.add(decision)
    session.commit()
