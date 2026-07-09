from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.domain.models.inventory import Placement, PlacementStatus, PlacementType, Publisher, PublisherStatus
from core.schemas.inventory import PlacementCreate, PublisherCreate
from infra.repositories.inventory_repository import PlacementRepository, PublisherRepository


class InventoryService:
    def __init__(self, session: Session) -> None:
        self.publisher_repository = PublisherRepository(session)
        self.placement_repository = PlacementRepository(session)

    def list_publishers(self) -> list[Publisher]:
        return self.publisher_repository.list_all()

    def create_publisher(self, payload: PublisherCreate) -> Publisher:
        publisher_name = payload.name.strip()
        if not publisher_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Publisher name cannot be empty",
            )
        publisher = Publisher(name=publisher_name, status=PublisherStatus(payload.status))
        try:
            return self.publisher_repository.create(publisher)
        except IntegrityError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Publisher name already exists",
            ) from exc

    def list_placements(self, publisher_id: int | None = None) -> list[Placement]:
        return self.placement_repository.list_all(publisher_id=publisher_id)

    def create_placement(self, payload: PlacementCreate) -> Placement:
        publisher = self.publisher_repository.get_by_id(payload.publisher_id)
        if publisher is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Publisher not found",
            )
        placement_name = payload.name.strip()
        if not placement_name:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Placement name cannot be empty",
            )
        placement = Placement(
            publisher_id=payload.publisher_id,
            name=placement_name,
            placement_type=PlacementType(payload.placement_type),
            status=PlacementStatus(payload.status),
        )
        return self.placement_repository.create(placement)
