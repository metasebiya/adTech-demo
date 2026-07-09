from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from core.domain.models import AuctionDecision, BidRequest, Campaign, Placement, Publisher, User
from core.domain.models.auction import DecisionStatus
from infra.db.init_db import seed_demo_auction_history, seed_demo_campaigns, seed_demo_inventory, seed_demo_users


def build_session() -> Session:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    from core.domain.models import Base

    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    return TestingSessionLocal()


def test_seed_data_matches_demo_shape() -> None:
    with build_session() as session:
        seed_demo_users(session)
        seed_demo_inventory(session)
        seed_demo_campaigns(session)
        seed_demo_auction_history(session)

        assert session.query(User).count() == 4
        assert session.query(Publisher).count() == 3
        assert session.query(Placement).count() == 4
        assert session.query(Campaign).count() == 5
        assert session.query(BidRequest).count() == 5
        assert session.query(AuctionDecision).filter(AuctionDecision.decision_status == DecisionStatus.win).count() >= 2
        assert session.query(AuctionDecision).filter(AuctionDecision.decision_status == DecisionStatus.no_bid).count() >= 2


def test_seed_data_is_idempotent_per_table() -> None:
    with build_session() as session:
        seed_demo_users(session)
        seed_demo_inventory(session)
        seed_demo_campaigns(session)
        seed_demo_auction_history(session)

        seed_demo_users(session)
        seed_demo_inventory(session)
        seed_demo_campaigns(session)
        seed_demo_auction_history(session)

        assert session.query(User).count() == 4
        assert session.query(Publisher).count() == 3
        assert session.query(Placement).count() == 4
        assert session.query(Campaign).count() == 5
        assert session.query(BidRequest).count() == 5
