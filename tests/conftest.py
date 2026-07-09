from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.main import app
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
from core.domain.models.campaign import CampaignStatus, DeviceType
from core.domain.models.inventory import PlacementStatus, PlacementType, PublisherStatus
from core.domain.models.user import UserRole
from infra.db.session import get_db_session


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        seed_publisher = Publisher(
            name="Seed Publisher",
            status=PublisherStatus.active,
        )
        db.add(seed_publisher)
        db.flush()

        seed_placement = Placement(
            publisher_id=seed_publisher.id,
            name="Seed Placement",
            placement_type=PlacementType.banner,
            status=PlacementStatus.active,
        )
        db.add(seed_placement)
        db.flush()

        db.add_all(
            [
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
        )
        db.flush()
        admin_user = db.query(User).filter(User.email == "admin@adtech-demo.local").one()
        db.add(
            Campaign(
                name="Seed Campaign",
                advertiser_name="Seed Advertiser",
                status=CampaignStatus.active,
                bid_cpm="2.50",
                daily_budget="100.00",
                remaining_budget="80.00",
                frequency_cap=1,
                created_by_user_id=admin_user.id,
                targets=[
                    CampaignTarget(
                        country="US",
                        device_type=DeviceType.desktop,
                        placement_id=seed_placement.id,
                    )
                ],
            )
        )
        db.flush()
        seed_campaign = db.query(Campaign).filter(Campaign.name == "Seed Campaign").one()
        bid_request = BidRequest(
            publisher_id=seed_publisher.id,
            placement_id=seed_placement.id,
            country="US",
            device_type=DeviceType.desktop,
            user_id="existing-user",
        )
        db.add(bid_request)
        db.flush()
        db.add(
            AuctionDecision(
                bid_request_id=bid_request.id,
                winner_campaign_id=seed_campaign.id,
                decision_status=DecisionStatus.win,
                clearing_price=seed_campaign.bid_cpm,
                decision_reason=seed_campaign.name,
                candidates=[
                    AuctionCandidate(
                        campaign_id=seed_campaign.id,
                        eligibility_status=CandidateStatus.eligible,
                        rejection_reason=None,
                        score=seed_campaign.bid_cpm,
                    )
                ],
            )
        )
        db.flush()
        seeded_decision = db.query(AuctionDecision).filter(AuctionDecision.bid_request_id == bid_request.id).one()
        db.add_all(
            [
                ImpressionEvent(
                    auction_decision_id=seeded_decision.id,
                    campaign_id=seed_campaign.id,
                    publisher_id=seed_publisher.id,
                    placement_id=seed_placement.id,
                    user_id="existing-user",
                    revenue="1.25",
                ),
                ClickEvent(
                    auction_decision_id=seeded_decision.id,
                    campaign_id=seed_campaign.id,
                ),
                ConversionEvent(
                    auction_decision_id=seeded_decision.id,
                    campaign_id=seed_campaign.id,
                    conversion_value="9.99",
                ),
            ]
        )
        db.commit()
        yield db


@pytest.fixture
def client(session: Session) -> Generator[TestClient, None, None]:
    def override_get_db_session():
        yield session

    app.dependency_overrides[get_db_session] = override_get_db_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
