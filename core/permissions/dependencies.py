from collections.abc import Callable
from typing import Annotated

from fastapi import Depends, HTTPException, status

from core.auth.security import get_current_user
from core.domain.models.user import User
from core.permissions.roles import ROLE_PERMISSIONS


def require_permissions(*permissions: str) -> Callable[[Annotated[User, Depends(get_current_user)]], User]:
    def dependency(current_user: Annotated[User, Depends(get_current_user)]) -> User:
        granted_permissions = ROLE_PERMISSIONS.get(current_user.role, set())
        if not set(permissions).issubset(granted_permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action",
            )
        return current_user

    return dependency
