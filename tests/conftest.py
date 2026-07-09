from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from apps.api.main import app
from core.auth.security import hash_password
from core.domain.models import Base, User
from core.domain.models.user import UserRole
from infra.db.session import get_db_session


@pytest.fixture
def session() -> Generator[Session, None, None]:
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, class_=Session)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        db.add(
            User(
                email="admin@adtech-demo.local",
                full_name="Admin User",
                password_hash=hash_password("ChangeMe123!"),
                role=UserRole.admin,
                is_active=True,
            )
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
