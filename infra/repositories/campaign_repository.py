from sqlalchemy.orm import Session, selectinload

from core.domain.models.campaign import Campaign


class CampaignRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_all(self) -> list[Campaign]:
        return (
            self.session.query(Campaign)
            .options(selectinload(Campaign.targets))
            .order_by(Campaign.id.asc())
            .all()
        )

    def get_by_id(self, campaign_id: int) -> Campaign | None:
        return (
            self.session.query(Campaign)
            .options(selectinload(Campaign.targets))
            .filter(Campaign.id == campaign_id)
            .one_or_none()
        )

    def create(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        return self.get_by_id(campaign.id) or campaign

    def save(self, campaign: Campaign) -> Campaign:
        self.session.add(campaign)
        self.session.commit()
        self.session.refresh(campaign)
        return self.get_by_id(campaign.id) or campaign
