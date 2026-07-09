from fastapi import APIRouter, Depends, HTTPException, status

from core.domain.services.auth_service import AuthService
from core.auth.security import get_current_user
from core.schemas.auth import LoginRequest, LoginResponse, UserRead
from infra.db.session import get_db_session

router = APIRouter()


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, session=Depends(get_db_session)) -> LoginResponse:
    auth_service = AuthService(session)
    user = auth_service.authenticate_user(payload.email, payload.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    token = auth_service.create_access_token_for_user(user)
    return LoginResponse(access_token=token, user=UserRead.model_validate(user))


@router.post("/logout")
def logout() -> dict[str, str]:
    return {"message": "Logout acknowledged on client. Server-side token revocation is not enabled in this demo."}


@router.get("/me", response_model=UserRead)
def me(current_user=Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
