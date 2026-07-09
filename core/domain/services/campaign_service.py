from decimal import Decimal

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from core.domain.models.campaign import Campaign, CampaignStatus, CampaignTarget, DeviceType
from core.domain.models.user import User
from core.schemas.campaign import CampaignCreate, CampaignTargetCreate, CampaignUpdate
from infra.repositories.campaign_repository import CampaignRepository
from infra.repositories.inventory_repository import PlacementRepository


class CampaignService:
    def __init__(self, session: Session) -> None:
        self.campaign_repository = CampaignRepository(session)
        self.placement_repository = PlacementRepository(session)

    def list_campaigns(self) -> list[Campaign]:
        return self.campaign_repository.list_all()

    def get_campaign(self, campaign_id: int) -> Campaign:
        campaign = self.campaign_repository.get_by_id(campaign_id)
        if campaign is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Campaign not found")
        return campaign

    def create_campaign(self, payload: CampaignCreate, current_user: User) -> Campaign:
        self._validate_budget(payload.daily_budget, payload.remaining_budget)
        campaign = Campaign(
            name=self._require_text(payload.name, "Campaign name"),
            advertiser_name=self._require_text(payload.advertiser_name, "Advertiser name"),
            status=CampaignStatus(payload.status),
            bid_cpm=payload.bid_cpm,
            daily_budget=payload.daily_budget,
            remaining_budget=payload.remaining_budget,
            frequency_cap=payload.frequency_cap,
            created_by_user_id=current_user.id,
        )
        campaign.targets = self._build_targets(payload.targets)
        return self.campaign_repository.create(campaign)

    def update_campaign(self, campaign_id: int, payload: CampaignUpdate) -> Campaign:
        campaign = self.get_campaign(campaign_id)

        if payload.name is not None:
            campaign.name = self._require_text(payload.name, "Campaign name")
        if payload.advertiser_name is not None:
            campaign.advertiser_name = self._require_text(payload.advertiser_name, "Advertiser name")
        if payload.status is not None:
            campaign.status = CampaignStatus(payload.status)
        if payload.bid_cpm is not None:
            campaign.bid_cpm = payload.bid_cpm
        if payload.daily_budget is not None:
            campaign.daily_budget = payload.daily_budget
        if payload.remaining_budget is not None:
            campaign.remaining_budget = payload.remaining_budget
        if payload.frequency_cap is not None:
            campaign.frequency_cap = payload.frequency_cap

        self._validate_budget(campaign.daily_budget, campaign.remaining_budget)

        if payload.targets is not None:
            campaign.targets.clear()
            campaign.targets.extend(self._build_targets(payload.targets))

        return self.campaign_repository.save(campaign)

    def _build_targets(self, targets: list[CampaignTargetCreate]) -> list[CampaignTarget]:
        placement_ids = {target.placement_id for target in targets}
        existing_ids = {placement.id for placement in self.placement_repository.list_by_ids(list(placement_ids))}
        missing_ids = sorted(placement_ids - existing_ids)
        if missing_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Placement ids not found: {', '.join(str(item) for item in missing_ids)}",
            )

        return [
            CampaignTarget(
                country=target.country.strip().upper(),
                device_type=DeviceType(target.device_type),
                placement_id=target.placement_id,
            )
            for target in targets
        ]

    @staticmethod
    def _validate_budget(daily_budget: Decimal, remaining_budget: Decimal) -> None:
        if remaining_budget > daily_budget:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Remaining budget cannot exceed daily budget",
            )

    @staticmethod
    def _require_text(value: str, label: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{label} cannot be empty",
            )
        return cleaned
