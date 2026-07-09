from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.domain.models.inventory import Placement, Publisher


class PublisherRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Publisher]:
        return self.session.query(Publisher).order_by(Publisher.id.asc()).all()

    def create(self, publisher: Publisher) -> Publisher:
        try:
            self.session.add(publisher)
            self.session.commit()
            self.session.refresh(publisher)
            return publisher
        except IntegrityError:
            self.session.rollback()
            raise

    def get_by_id(self, publisher_id: int) -> Publisher | None:
        return self.session.query(Publisher).filter(Publisher.id == publisher_id).one_or_none()


class PlacementRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self, publisher_id: int | None = None) -> list[Placement]:
        query = self.session.query(Placement).order_by(Placement.id.asc())
        if publisher_id is not None:
            query = query.filter(Placement.publisher_id == publisher_id)
        return query.all()

    def create(self, placement: Placement) -> Placement:
        try:
            self.session.add(placement)
            self.session.commit()
            self.session.refresh(placement)
            return placement
        except IntegrityError:
            self.session.rollback()
            raise

    def list_by_ids(self, placement_ids: list[int]) -> list[Placement]:
        if not placement_ids:
            return []
        return self.session.query(Placement).filter(Placement.id.in_(placement_ids)).all()
