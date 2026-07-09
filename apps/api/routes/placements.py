from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from core.domain.models.user import User
from core.domain.services.inventory_service import InventoryService
from core.permissions.dependencies import require_permissions
from core.permissions.roles import MANAGE_PUBLISHERS_AND_PLACEMENTS
from core.schemas.inventory import PlacementCreate, PlacementRead
from infra.db.session import get_db_session

router = APIRouter()


@router.get("", response_model=list[PlacementRead])
def list_placements(
    _: Annotated[User, Depends(require_permissions(MANAGE_PUBLISHERS_AND_PLACEMENTS))],
    session: Session = Depends(get_db_session),
    publisher_id: int | None = Query(default=None),
) -> list[PlacementRead]:
    service = InventoryService(session)
    return [
        PlacementRead.model_validate(placement)
        for placement in service.list_placements(publisher_id=publisher_id)
    ]


@router.post("", response_model=PlacementRead, status_code=201)
def create_placement(
    payload: PlacementCreate,
    _: Annotated[User, Depends(require_permissions(MANAGE_PUBLISHERS_AND_PLACEMENTS))],
    session: Session = Depends(get_db_session),
) -> PlacementRead:
    service = InventoryService(session)
    placement = service.create_placement(payload)
    return PlacementRead.model_validate(placement)
