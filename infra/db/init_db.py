from sqlalchemy.orm import Session

from core.auth.security import hash_password
from core.domain.models import Base, User
from core.domain.models.user import UserRole
from infra.db.session import engine


def initialize_database() -> None:
    Base.metadata.create_all(bind=engine)
    with Session(bind=engine) as session:
        seed_demo_users(session)


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
