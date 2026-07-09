from sqlalchemy.orm import Session

from core.domain.models.event import ClickEvent, ConversionEvent, ImpressionEvent


class ImpressionEventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, event: ImpressionEvent) -> ImpressionEvent:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_all(self) -> list[ImpressionEvent]:
        return self.session.query(ImpressionEvent).order_by(ImpressionEvent.created_at.desc()).all()


class ClickEventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, event: ClickEvent) -> ClickEvent:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_all(self) -> list[ClickEvent]:
        return self.session.query(ClickEvent).order_by(ClickEvent.created_at.desc()).all()


class ConversionEventRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create(self, event: ConversionEvent) -> ConversionEvent:
        self.session.add(event)
        self.session.commit()
        self.session.refresh(event)
        return event

    def list_all(self) -> list[ConversionEvent]:
        return self.session.query(ConversionEvent).order_by(ConversionEvent.created_at.desc()).all()
