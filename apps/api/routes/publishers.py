from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.inventory_service import InventoryService
from core.permissions.dependencies import require_permissions
from core.permissions.roles import MANAGE_PUBLISHERS_AND_PLACEMENTS
from core.schemas.inventory import PublisherCreate, PublisherRead
from infra.db.session import get_db_session

router = APIRouter()


@router.get("", response_model=list[PublisherRead])
def list_publishers(
    _: Annotated[User, Depends(require_permissions(MANAGE_PUBLISHERS_AND_PLACEMENTS))],
    session: Session = Depends(get_db_session),
) -> list[PublisherRead]:
    service = InventoryService(session)
    return [PublisherRead.model_validate(publisher) for publisher in service.list_publishers()]


@router.post("", response_model=PublisherRead, status_code=201)
def create_publisher(
    payload: PublisherCreate,
    _: Annotated[User, Depends(require_permissions(MANAGE_PUBLISHERS_AND_PLACEMENTS))],
    session: Session = Depends(get_db_session),
) -> PublisherRead:
    service = InventoryService(session)
    publisher = service.create_publisher(payload)
    return PublisherRead.model_validate(publisher)
