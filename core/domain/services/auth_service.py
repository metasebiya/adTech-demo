from datetime import datetime, timezone

from sqlalchemy.orm import Session

from core.auth.security import create_access_token, verify_password
from core.domain.models.user import User
from infra.repositories.user_repository import UserRepository


class AuthService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.user_repository = UserRepository(session)

    def authenticate_user(self, email: str, password: str) -> User | None:
        user = self.user_repository.get_by_email(email)
        if user is None or not user.is_active:
            return None
        if not verify_password(password, user.password_hash):
            return None
        user.last_login_at = datetime.now(timezone.utc)
        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)
        return user

    def create_access_token_for_user(self, user: User) -> str:
        return create_access_token(subject=user.email)
